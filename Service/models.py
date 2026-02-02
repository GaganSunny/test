from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    servicer_name = models.CharField(max_length=100)
    callable_of = models.TextField()
    password = models.CharField(max_length=100, default="thisisapassword")
    mobile_number = models.CharField(max_length=10)
    def save(self, *args, **kwargs):
        if not self.user:
            # create a default user account
            username = self.servicer_name.lower().replace(" ", "_")
            password = self.password
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                password=password
            )
            user.is_staff = False  # Service providers are NOT staff
            user.save()
            self.user = user
        super().save(*args, **kwargs)

    def __str__(self):
        return self.servicer_name

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('RejectedByProvider', 'Rejected by Provider'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=200)
    address = models.TextField(default="")
    message = models.TextField(blank=True)
    amount = models.PositiveIntegerField(default=250)  # fixed ₹250 charge
    created_at = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=100, blank=True)  # Razorpay payment id
    payment_status = models.CharField(max_length=50, default='Pending')
    service_provider = models.ForeignKey(
        'ServiceProvider', on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    pin = models.CharField(max_length=4, blank=True, null=True)  # 4-digit completion PIN

    # New fields for latitude and longitude
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    @property
    def add_user_number(self):
        return self.user.last_name
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username} - Status: {self.status}"

    def save(self, *args, **kwargs):
        if not self.pin:
            self.pin = get_random_string(length=4, allowed_chars='0123456789')
        super().save(*args, **kwargs)
    