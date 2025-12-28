from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from hotels.models import Restaurant
from django.contrib import messages
from django.contrib.auth.models import User
from .models import User
from django.conf import settings
from django.core.mail import send_mail



def owner_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            
            restaurant = Restaurant.objects.filter(owner=user).first()

            if restaurant and restaurant.status == 'APPROVED':
                return redirect('hotels:owner_dashboard')
            else:
                return render(request, 'accounts/login.html', {
                    'error': 'Your restaurant is waiting for admin approval.'
                })

        return render(request, 'accounts/login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'accounts/login.html')


def owner_logout(request):
    logout(request)
    return redirect('home')


 
def customer_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('accounts:customer_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('accounts:customer_register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            user_type='customer'
        )

        

        login(request, user)
        messages.success(request, "Registration successful")
        return redirect('home')

    return render(request, "accounts/customer_register.html")

def customer_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "accounts/customer_login.html")


def customer_logout(request):
    logout(request)
    return redirect("hotels:hotel_list")

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_superuser:
            login(request, user)
            messages.success(request, "Admin login successful")
            return redirect("home")
        else:
            messages.error(request, "Only admins can login here")

    return render(request, "accounts/admin_login.html")

    
    
