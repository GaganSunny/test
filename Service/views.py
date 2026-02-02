from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.conf import settings
import razorpay
import json
import hmac
import hashlib
from .forms import SignUpForm
from .models import Order, ServiceProvider
from django.contrib.admin.views.decorators import staff_member_required
# import pywhatkit
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LogoutView
from django.views.decorators.csrf import csrf_protect
import requests

services_detail = {
    'Home machinery Service': 'house.png',
    'Plumbing': 'technician.png',
    'Electrician': 'electrician.png',
    'T.V Repair': 'cinema.png',
    'Refrigerator Repair': 'cold.png',
    'Air Cooler Repair': 'air-cooler.png',
    'Computer Repair': 'computer_repair.png',
    'Barber': 'hairdresser.png',
    'Beautionist': 'makeup.png',
    'Welding Work': 'welding.png',
    'AC Service': 'air-conditioner.png',
    'Water Filter Service': 'purified-water.png',
    'CC Camera Service': 'cctv.png',
    'Septic Tank Service': 'septic-tank.png',
    'Cupboard Service': 'cabinet.png',
    'Glass Work Services': 'window.png',
    'Blood and Body Checkup': 'standing-human-body-silhouette.png',
    'Cleaning Services': 'broom.png',
    'POP service': 'construction.png',
    'Helper': 'nurse.png',
    'Packing and Moving Goods': 'delivery-truck.png',
    'Door Polishing': 'door (1).png',
    'Washing Services': 'washing-clothes.png',
    'Door Designing': 'door.png',
    'Showcase Designing': 'window-display.png',
    'Tails Services': 'parquet.png',
    'Flooring Work': 'hammer.png',
    'Gas Stove Repair': 'stove.png',
    'Glass Fitting Service': 'window-frame.png'
}
@require_POST
@login_required
def accept_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, service_provider__user=request.user)
    order.status = 'Accepted'
    order.save()
    return redirect('service_provider_dashboard')

@require_POST
@login_required
def reject_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, service_provider__user=request.user)
    order.status = 'RejectedByProvider'
    order.service_provider = None  # Remove assigned provider so admin can reassign
    order.save()
    return redirect('service_provider_dashboard')

services_list = list(services_detail.keys())

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required(login_url='login')
def index(request):
    services = []
    for name in services_list:
        image_file = services_detail.get(name, '')
        image_path = f'service/images/{image_file}' if image_file else 'images/default.png'
        services.append({
            'name': name,
            'image': image_path,
        })
    return render(request, 'index.html', {'services': services})


def login(request):
    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def services(request):
    return render(request, 'services.html', {'services_list': services_list})


@login_required
def service_product(request):
    service_name = request.GET.get('name')
    context = {
        'service_name': service_name,
        'services_list': services_list,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'service_detail.html', context)

@csrf_exempt
@login_required
def reverse_geocode(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    if not lat or not lon:
        return JsonResponse({'error': 'Latitude and longitude are required.'}, status=400)

    try:
        response = requests.get(
            f"https://nominatim.openstreetmap.org/reverse",
            params={'lat': lat, 'lon': lon, 'format': 'json'},
            headers={'User-Agent': 'YourAppName/1.0 (your@email.com)'}
        )
        response.raise_for_status()
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@require_POST
@staff_member_required
def cancel_order_by_admin(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "Cancelled"
    order.save()
    return redirect('admin_dashbord')

@login_required
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, service_provider=request.user.serviceprovider)
    if request.method == "POST":
        order.status = 'Completed'
        order.save()
    return redirect('service_provider_dashboard')
@login_required
@require_POST
def verify_completion_pin(request, order_id):
    input_pin = request.POST.get('pin')
    try:
        order = Order.objects.get(id=order_id, service_provider=request.user.serviceprovider)
        if input_pin == order.pin:
            order.status = 'Completed'
            order.save()
            return redirect('service_provider_dashboard')
        else:
            return HttpResponseForbidden("Incorrect PIN.")
    except Order.DoesNotExist:
        return HttpResponseForbidden("Order not found or unauthorized.")

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

def submit_order(request):
    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        order = Order(service_name=service_name, address=address, latitude=latitude, longitude=longitude)
        order.save()

        return redirect('order_success')

    return HttpResponseBadRequest('Invalid request')

def order_success(request):
    return render(request, 'order_success.html')

@login_required
def create_order(request):
    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        address = request.POST.get('address')
        payment_id = request.POST.get('payment_id')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Optional: validate inputs here (check if latitude and longitude exist)

        Order.objects.create(
            user=request.user,
            service_name=service_name,
            address=address,
            payment_id=payment_id,
            payment_status="Paid",
            latitude=latitude,
            longitude=longitude
        )
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)
def payment_success(request):
    return render(request, 'payment_success.html')

@staff_member_required
def admin_dashbord(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        provider_id = request.POST.get("provider_id")

        try:
            order = Order.objects.get(id=order_id)
            provider = ServiceProvider.objects.get(id=provider_id)
            order.service_provider = provider
            order.status = "Assigned"
            order.save()
        except (Order.DoesNotExist, ServiceProvider.DoesNotExist):
            # Optional: Add error message handling here
            pass

        return redirect('admin_dashbord')

    # Include both Pending and RejectedByProvider orders
    pending_orders = Order.objects.filter(status__in=["Pending", "RejectedByProvider"])
    service_providers = ServiceProvider.objects.all()

    return render(request, "admin_dashbord.html", {
        "orders": pending_orders,
        "service_providers": service_providers,
    })


@login_required
def service_provider_dashboard(request):
    try:
        service_provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        return HttpResponseForbidden("You are not authorized.")

    new_orders = Order.objects.filter(service_provider=service_provider, status='Assigned')
    pending_orders = Order.objects.filter(service_provider=service_provider, status='Accepted')

    return render(request, 'service_provider_dashboard.html', {
        'new_orders': new_orders,
        'pending_orders': pending_orders,
    })

@method_decorator(csrf_protect, name='dispatch')
class PostLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        return self.logout(request, *args, **kwargs)