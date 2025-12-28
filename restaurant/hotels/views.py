from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Avg
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from datetime import datetime

from accounts.models import User
from accounts.decorators import admin_required
from .models import Restaurant, MenuItem, Order, Review, OrderItem, TableBooking
from .forms import RestaurantForm, MenuItemForm

# ───────────────────────────────────────────────
# HOME PAGE
# ───────────────────────────────────────────────
def home(request):
    all_hotels = Restaurant.objects.filter(status='APPROVED')
    return render(request, 'home.html', {'hotels': all_hotels})


# ───────────────────────────────────────────────
# HOTEL LIST
# ───────────────────────────────────────────────
def hotel_list(request):
    hotel_type = request.GET.get('type', '')
    rating = request.GET.get('rating', '')
    location = request.GET.get('location', '')

    hotels = Restaurant.objects.filter(status='APPROVED')

    if hotel_type:
        hotels = hotels.filter(restaurant_type=hotel_type)

    if rating:
        try:
            hotels = hotels.filter(rating__gte=float(rating))
        except ValueError:
            pass

    if location:
        hotels = hotels.filter(location__icontains=location)

    return render(request, 'hotels/hotel_list.html', {'hotels': hotels})


# ───────────────────────────────────────────────
# HOTEL DETAIL
# ───────────────────────────────────────────────
def hotel_detail(request, hotel_id):
    restaurant = get_object_or_404(Restaurant, id=hotel_id, status='APPROVED')
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    reviews = Review.objects.filter(restaurant=restaurant)

    return render(request, 'hotels/hotel_detail.html', {
        'hotel': restaurant,
        'menu_items': menu_items,
        'reviews': reviews,
        'real_restaurant_id': restaurant.id
    })


# ───────────────────────────────────────────────
# OWNER DASHBOARD
# ───────────────────────────────────────────────


@login_required
def owner_dashboard(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    if not restaurant:
        return redirect('hotels:owner_register')

    orders = Order.objects.filter(restaurant=restaurant)
    total_earnings = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    reviews = Review.objects.filter(restaurant=restaurant)
    table_bookings = TableBooking.objects.filter(restaurant=restaurant).select_related("user").order_by('-created_at')

    
    

    return render(request, 'hotels/owner_dashboard.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'orders': orders,
        'reviews': reviews,
        'total_earnings': total_earnings,
        'table_bookings': table_bookings,  
    })


# ───────────────────────────────────────────────
# MENU MANAGEMENT
# ───────────────────────────────────────────────
@login_required
def add_menu_item(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    if restaurant.status != 'APPROVED':
        return redirect('hotels:owner_dashboard')

    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.restaurant = restaurant
            item.save()
            return redirect('hotels:owner_dashboard')
    else:
        form = MenuItemForm()

    return render(request, 'hotels/add_menu_item.html', {'form': form})


@login_required
def edit_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, restaurant__owner=request.user)

    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('hotels:owner_dashboard')
    else:
        form = MenuItemForm(instance=item)

    return render(request, 'hotels/edit_menu_item.html', {'form': form})


@login_required
def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, restaurant__owner=request.user)
    item.delete()
    return redirect('hotels:owner_dashboard')


# ───────────────────────────────────────────────
# OWNER AUTH
# ───────────────────────────────────────────────
def owner_login(request):
    context = {}
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('hotels:owner_dashboard')
        context['error'] = 'Invalid credentials'
    return render(request, 'hotels/owner_login.html', context)


def owner_logout(request):
    logout(request)
    return redirect('hotels:owner_login')


def owner_register(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            context['error'] = 'Passwords do not match'
            return render(request, 'hotels/owner_register.html', context)

        if User.objects.filter(username=username).exists():
            context['error'] = 'Username already exists'
            return render(request, 'hotels/owner_register.html', context)

        user = User.objects.create_user(username=username, email=email, password=password, user_type='owner')
        login(request, user)

        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = user
            restaurant.status = 'PENDING'
            restaurant.save()
            return redirect('hotels:owner_dashboard')

        context['form'] = form
        return render(request, 'hotels/owner_register.html', context)

    context['form'] = RestaurantForm()
    return render(request, 'hotels/owner_register.html', context)


# ───────────────────────────────────────────────
# REVIEWS
# ───────────────────────────────────────────────


@login_required
def reviews_page(request, hotel_id):
    restaurant = get_object_or_404(Restaurant, id=hotel_id)

    
    if request.method == 'POST':
        user_name = request.POST.get('user')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if user_name and rating and comment:
            Review.objects.create(
                restaurant=restaurant,
                user=user_name,
                rating=int(rating),
                comment=comment
            )

    
    reviews = Review.objects.filter(restaurant=restaurant).order_by('-created_at')

    
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    avg_rating = round(avg_rating, 2)

    context = {
        'hotel': restaurant,
        'reviews': reviews,
        'avg_rating': avg_rating
    }

    return render(request, 'hotels/review.html', context)




# ───────────────────────────────────────────────
# CART FUNCTIONS
# ───────────────────────────────────────────────

def cart_add(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    cart = request.session.get("cart", {})
    cart.setdefault("restaurant_id", item.restaurant.id)
    cart.setdefault("items", {})
    item_id_str = str(item.id)

    if item_id_str in cart["items"]:
        cart["items"][item_id_str]["quantity"] += 1
    else:
        cart["items"][item_id_str] = {
            "name": item.name,
            "price": float(item.price),
            "image": item.image.url if item.image else "",
            "quantity": 1
        }

    request.session["cart"] = cart
    return HttpResponse("added", status=200)


def cart_page(request):
    cart = request.session.get("cart", {})
    items = cart.get("items", {}).values() if cart else []
    subtotal = sum(i["price"] * i["quantity"] for i in items)
    return render(request, "hotels/cart_page.html", {
        "items": items,
        "subtotal": subtotal
    })


def clear_cart(request):
    request.session.pop("cart", None)
    return redirect("hotels:cart_page")


def place_order(request):
    cart = request.session.get("cart", {})
    if not cart or not cart.get("items"):
        messages.error(request, "Your cart is empty.")
        return redirect("hotels:hotel_list")

    restaurant = get_object_or_404(Restaurant, id=cart.get("restaurant_id"))
    total = sum(i["price"] * i["quantity"] for i in cart["items"].values())

    
    order = Order.objects.create(
        restaurant=restaurant,
        user=None,
        total_price=total,
        status="PENDING",
        payment_method=request.POST.get("payment_method", "OFFLINE")
    )

    for item_id, item_data in cart["items"].items():
        menu_item = get_object_or_404(MenuItem, id=item_id)
        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=item_data["quantity"],
            price=menu_item.price
        )

    request.session.pop("cart", None)
    messages.success(request, "Order placed! Waiting for owner confirmation.")
      

    return redirect("hotels:my_reservations")


@login_required
def order_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.select_related("menu_item")
    subtotal = sum(item.price * item.quantity for item in order_items)
    gst = subtotal * Decimal("0.05")
    total = subtotal + gst

    return render(request, "hotels/order_receipt.html", {
        "order": order,
        "order_items": order_items,
        "subtotal": subtotal,
        "gst": gst,
        "total": total
    })


# ───────────────────────────────────────────────
# TABLE BOOKINGS
# ───────────────────────────────────────────────

@login_required
def book_table(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == "POST":
        booking_date = request.POST.get("booking_date")
        booking_time = request.POST.get("booking_time")
        guests = request.POST.get("guests")

        if not (booking_date and booking_time and guests):
            messages.error(request, "Please fill in all fields.")
            return redirect("hotels:book_table", restaurant_id=restaurant.id)

        booking = TableBooking.objects.create(
            restaurant=restaurant,
            user=request.user,
            booking_date=booking_date,
            booking_time=booking_time,
            guests=guests,
            status="PENDING"
        )

        messages.success(request, "Booking confirmed!")
        return redirect("hotels:booking_summary", booking_id=booking.id)

    return render(request, "hotels/book_table.html", {"restaurant": restaurant})

def booking_summary(request, booking_id):
    booking = get_object_or_404(TableBooking, id=booking_id)
    return render(request, "hotels/booking_summary.html", {"reservation": booking})

# ───────────────────────────────────────────────
# MY RESERVATIONS
# ───────────────────────────────────────────────
@login_required
def my_reservations(request):
    reservations = TableBooking.objects.filter(
        user=request.user
    ).select_related("restaurant", "user").order_by("-created_at")

    return render(request, "hotels/my_reservations.html", {
        "reservations": reservations
    })


@login_required
def my_reservations_ajax(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    orders_data = []

    for order in orders:
        if order.status == "PENDING":
            color, text = "#ffc107", "Pending"
        elif order.status == "ACCEPTED":
            color, text = "#28a745", "Accepted"
        elif order.status == "REJECTED":
            color, text = "#dc3545", "Rejected"
        else:
            color, text = "#007bff", "Completed"

        orders_data.append({
            "id": order.id,
            "status_text": text,
            "status_color": color,
            "name": request.user.username,
            "date": order.created_at.date(),
            "time": order.created_at.time(),
            "guests": order.items.count(),
            "hotel_name": order.restaurant.name,
        })

    return JsonResponse({"orders": orders_data})


# ───────────────────────────────────────────────
# ADMIN DASHBOARD
# ───────────────────────────────────────────────
@admin_required
def admin_dashboard(request):
    status_filter = request.GET.get('status')
    if status_filter in ['PENDING', 'APPROVED', 'REJECTED']:
        restaurants = Restaurant.objects.filter(status=status_filter)
    else:
        restaurants = Restaurant.objects.all()

    return render(request, 'hotels/admin_dashboard.html', {
        'restaurants': restaurants,
        'pending_count': Restaurant.objects.filter(status='PENDING').count(),
        'approved_count': Restaurant.objects.filter(status='APPROVED').count(),
        'rejected_count': Restaurant.objects.filter(status='REJECTED').count(),
    })


@admin_required
def approve_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    restaurant.status = "APPROVED"
    restaurant.save()
    return redirect("hotels:admin_dashboard")


@admin_required
def reject_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    restaurant.status = "REJECTED"
    restaurant.save()
    return redirect("hotels:admin_dashboard")


@admin_required
@require_http_methods(["POST"])
def delete_restaurant(request, restaurant_id):
    Restaurant.objects.filter(id=restaurant_id).delete()
    messages.success(request, "Restaurant deleted successfully.")
    return redirect("hotels:admin_dashboard")


# ───────────────────────────────────────────────
# MAP PAGE
# ───────────────────────────────────────────────
@login_required
def map_page(request, hotel_id):
    restaurant = get_object_or_404(Restaurant, id=hotel_id)
    return render(request, 'hotels/map_page.html', {'restaurant': restaurant})


@csrf_exempt
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            status = data.get("status")
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"})

        if status in ["PENDING", "ACCEPTED", "REJECTED", "COMPLETED"]:
            order.status = status
            order.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Invalid status"})

    return JsonResponse({"success": False, "error": "Invalid request"})   
@login_required
def owner_bookings(request):
    bookings = TableBooking.objects.filter(
        restaurant__owner=request.user
    ).select_related("restaurant", "user").order_by("-created_at")

    return render(request, "hotels/owner_bookings.html", {
        "bookings": bookings
    })

   
@login_required
def update_booking_status(request, booking_id, action):
    booking = get_object_or_404(TableBooking, id=booking_id)

    
    if booking.restaurant.owner != request.user:
        return redirect("hotels:owner_bookings")

    if action == "accept":
        booking.status = "CONFIRMED"
    elif action == "reject":
        booking.status = "REJECTED"

    booking.save()
    return redirect("hotels:owner_bookings")

@login_required
def accept_booking(request, booking_id):
    booking = get_object_or_404(TableBooking, id=booking_id, restaurant__owner=request.user)
    booking.status = 'CONFIRMED'
    booking.save()
    return redirect('hotels:owner_dashboard')


@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(TableBooking, id=booking_id, restaurant__owner=request.user)
    booking.status = 'REJECTED'
    booking.save()
    return redirect('hotels:owner_dashboard')
