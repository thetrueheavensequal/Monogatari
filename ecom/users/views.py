from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout as authlogout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth import get_user_model
from shop.models import Order, Transaction
from django.contrib.auth.decorators import login_required
from .models import Profile, Address

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            if user is not None:
                # Authenticate the user with explicit backend
                authenticated_user = authenticate(
                    request, 
                    username=username, 
                    password=password,
                    backend='users.backends.CustomUserBackend'
                )
                if authenticated_user:
                    auth_login(request, authenticated_user)
                    return redirect('users:profile')
                else:
                    messages.error(request, 'Error during authentication.')
            else:
                messages.error(request, 'Error creating user.')
    return render(request, 'users/signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # First check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Account does not exist. Please sign up.')
            return redirect('users:signup')
            
        # Then try to authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None and not user.is_staff:
            try:
                # Ensure profile exists
                Profile.objects.get_or_create(user=user)
                auth_login(request, user)
                return redirect('users:profile')
            except Exception as e:
                messages.error(request, 'An error occurred during login. Please try again.')
                return redirect('users:login')
        else:
            messages.error(request, 'Invalid password.')
    
    return render(request, 'users/login.html')

def profile(request):
    return render(request, 'users/profile.html')

def logout(request):
    authlogout(request)
    return redirect('home')

@login_required
def new_orders(request):
    orders = Order.objects.filter(user=request.user, status='pending').order_by('-created_at')
    return render(request, 'users/new_orders.html', {'orders': orders})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).exclude(status='pending').order_by('-created_at')
    return render(request, 'users/order_history.html', {'orders': orders})

@login_required
def transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/transactions.html', {'transactions': transactions})

@login_required
def profile_settings(request):
    profile = request.user.profile
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        bio = request.POST.get('bio')
        profile_pic = request.FILES.get('profile_pic')
        phone = request.POST.get('phone')
        
        # Update user fields
        request.user.username = username
        request.user.email = email
        request.user.save()

        # Update profile fields
        profile.bio = bio
        if profile_pic:
            profile.profile_pic = profile_pic
        profile.phone = phone
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('users:profile')  # Redirect to profile page after saving
    return render(request, 'users/profile_settings.html', {'profile': profile})

@login_required
def add_address(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        
        if address and city and country:
            Address.objects.create(
                user=request.user,
                address=address,
                city=city,
                country=country
            )
            messages.success(request, 'Address added successfully.')
        return redirect('users:profile')
    return redirect('users:profile')

@login_required
def delete_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully.')
    return redirect('users:profile')

@login_required
def edit_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    if request.method == 'POST':
        address.address = request.POST.get('address')
        address.city = request.POST.get('city')
        address.country = request.POST.get('country')
        address.save()
        messages.success(request, 'Address updated successfully.')
        return redirect('users:profile')
    return render(request, 'users/edit_address.html', {'address': address})