import random
import razorpay
from django.http import JsonResponse
from django.db.models import Q
import random
import string
from django.http import QueryDict
from django.conf import settings
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from .models import Product, CartItem, WishlistItem, Order, Transaction, OrderItem
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as authlogin, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ContactForm  # Make sure this import exists
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .filters import ProductFilter

# Create your views here.
def base(request):
    return render(request, 'base.html')

def dress(request):
    return render(request, 'dress.html')

def skirts(request):
    return render(request, 'skirts.html')

def top(request):
    return render(request, 'top.html')

def pants(request):
    return render(request, 'pants.html')

def coats(request):
    return render(request, 'coats.html')

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def new(request):
    products = list(Product.objects.all())
    random_products = random.sample(products, min(3, len(products)))
    return render(request, 'new.html', {'random_products': random_products})

def contact(request):
    contact_info = None
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_info = form.save()
            form = ContactForm()  # Clear form after save
    else:
        form = ContactForm()
    return render(request, 'contact.html', {
        'form': form,
        'contact_info': contact_info
    })

def search(request):
    query = request.GET.get('q', '')
    results = []
    product_filter = None
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )
        from .filters import ProductFilter
        product_filter = ProductFilter(request.GET, queryset=results)
        results = product_filter.qs
        # AJAX auto-suggest
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            suggestions = list(results.values_list('name', flat=True)[:8])
            return JsonResponse({'suggestions': suggestions})
        # If a query is present, show results page
        return render(request, 'search-results.html', {
            'query': query,
            'results': results,
            'filter': product_filter,
        })
    # If no query, show search bar only
    return render(request, 'search.html')

def account(request):
    return render(request, 'users/signup.html')

def cart(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            quantity_action = request.POST.get('quantity_action')
            slug = request.POST.get('product_slug')
            if quantity_action and slug:
                cart_item = CartItem.objects.filter(user=request.user, product__slug=slug).first()
                if cart_item:
                    if quantity_action == 'increase':
                        cart_item.quantity += 1
                        cart_item.save()
                    elif quantity_action == 'decrease' and cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()
                return redirect('cart')

            remove_slug = request.POST.get('remove_slug')
            if remove_slug:
                CartItem.objects.filter(user=request.user, product__slug=remove_slug).delete()
                messages.success(request, "Removed from cart.")
                return redirect('cart')

            slug = request.POST.get('product_slug')
            if slug:
                product = get_object_or_404(Product, slug=slug)
                cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
                if not created:
                    cart_item.quantity += 1
                    cart_item.save()
                messages.success(request, f"{product.name} added to cart!")
            return redirect('cart')

        cart_items = CartItem.objects.filter(user=request.user)
        total = sum(item.product.price * item.quantity for item in cart_items)
    else:
        if 'cart' not in request.session:
            request.session['cart'] = {}

        cart = request.session['cart']

        if request.method == 'POST':
            quantity_action = request.POST.get('quantity_action')
            slug = request.POST.get('product_slug')
            if quantity_action and slug and slug in cart:
                if quantity_action == 'increase':
                    cart[slug] += 1
                elif quantity_action == 'decrease' and cart[slug] > 1:
                    cart[slug] -= 1
                request.session['cart'] = cart
                return redirect('cart')

            remove_slug = request.POST.get('remove_slug')
            if remove_slug and remove_slug in cart:
                cart.pop(remove_slug, None)
                request.session['cart'] = cart
                messages.success(request, "Removed from cart.")
                return redirect('cart')

            slug = request.POST.get('product_slug')
            if slug:
                cart[slug] = cart.get(slug, 0) + 1  # Increment quantity
                request.session['cart'] = cart
                product = get_object_or_404(Product, slug=slug)
                messages.success(request, f"{product.name} added to cart!")
            return redirect('cart')

        products = Product.objects.filter(slug__in=cart.keys())
        cart_items = []
        total = 0
        for product in products:
            quantity = cart[str(product.slug)]
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

    # Razorpay integration for checkout
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.POST.get("checkout") == "1":
            amount = int(float(total) * 100)
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })
            return JsonResponse({
                "razorpay_order_id": razorpay_order["id"],
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "amount": amount,
                "currency": "INR"
            })
        elif request.GET.get("clear") == "1":
            if request.user.is_authenticated:
                CartItem.objects.filter(user=request.user).delete()
            else:
                request.session['cart'] = {}
            return JsonResponse({"status": "cleared"})
        else:
            # Always return JSON for AJAX POSTs
            return JsonResponse({"error": "Invalid request"}, status=400)

    context = {
        'cart_items': cart_items,
        'total': total,
        'user_cart': request.user.is_authenticated,
        'razorpay_order': None,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'cart.html', context)

def wishlist(request):
    if request.user.is_authenticated:
        # User-based wishlist
        if request.method == 'POST':
            remove_slug = request.POST.get('remove_slug')
            if remove_slug:
                WishlistItem.objects.filter(user=request.user, product__slug=remove_slug).delete()
                messages.success(request, "Removed from wishlist.")
                return redirect('wishlist')

            slug = request.POST.get('product_slug')
            if slug:
                product = get_object_or_404(Product, slug=slug)
                WishlistItem.objects.get_or_create(user=request.user, product=product)
                messages.success(request, f"{product.name} added to wishlist!")
            return redirect('wishlist')

        wishlist_items = WishlistItem.objects.filter(user=request.user)
        return render(request, 'wishlist.html', {'wishlist_items': wishlist_items, 'user_wishlist': True})
    else:
        # Session-based wishlist
        if 'wishlist' not in request.session:
            request.session['wishlist'] = []
        wishlist = request.session['wishlist']

        if request.method == 'POST':
            remove_slug = request.POST.get('remove_slug')
            if remove_slug and remove_slug in wishlist:
                wishlist.remove(remove_slug)
                request.session['wishlist'] = wishlist
                messages.success(request, "Removed from wishlist.")
                return redirect('wishlist')

            slug = request.POST.get('product_slug')
            if slug and slug not in wishlist:
                wishlist.append(slug)
                request.session['wishlist'] = wishlist
                product = get_object_or_404(Product, slug=slug)
                messages.success(request, f"{product.name} added to wishlist!")
            return redirect('wishlist')

        products = Product.objects.filter(slug__in=wishlist)
        return render(request, 'wishlist.html', {'products': products, 'user_wishlist': False})

def collection(request):
    products = Product.objects.all()
    product_filter = ProductFilter(request.GET, queryset=products)
    filter_active = any(request.GET.get(key) for key in ['gender', 'category', 'min_price', 'max_price', 'name'])
    return render(request, 'collection.html', {
        'filter': product_filter,
        'products': product_filter.qs,
        'filter_active': filter_active,
    })

def my_orders(request):
    return render(request, 'my_orders.html')

def product_list(request, category=None):
    products = Product.objects.all()
    if category:
        products = products.filter(category=category)
    product_filter = ProductFilter(request.GET, queryset=products)
    return render(request, 'product_list.html', {
        'filter': product_filter,
        'category': category,
        'products': product_filter.qs,  # <-- Add this line
    })

# views.py

def product_filter(request):
    products = Product.objects.none()
    selected_gender = request.GET.getlist('gender')
    selected_types = request.GET.getlist('type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    type_choices = ["Shirts", "Pants", "Coats", "Skirts", "Tops", "Dresses"]
    filter_active = bool(selected_gender or selected_types or min_price or max_price)

    if filter_active:
        products = Product.objects.all()
        if selected_gender:
            products = products.filter(category__in=[g.lower() for g in selected_gender])
        if selected_types:
            categories = [t.lower()[:-1] if t.endswith('s') else t.lower() for t in selected_types]
            products = products.filter(category__in=categories)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

    from collections import defaultdict
    grouped_products = defaultdict(list)
    for product in products:
        display_name = product.get_category_display()
        if not display_name.endswith('s'):
            display_name += 's'
        grouped_products[display_name].append(product)

    return render(request, 'product_filter.html', {
        'grouped_products': grouped_products,
        'type_choices': type_choices,
        'selected_gender': selected_gender,
        'selected_types': selected_types,
        'min_price': min_price,
        'max_price': max_price,
        'filter_active': filter_active,
    })

def product_detail(request, category, slug):
    product = get_object_or_404(Product, category=category, slug=slug)
    sizes = product.sizes.split(',') if product.sizes else []
    return render(request, 'product_detail.html', {
        'product': product,
        'category': category,
        'sizes': sizes,
    })

def razorpay_checkout(request):
    if request.method == "POST":
        amount = int(float(request.POST.get("amount", "10.00")) * 100)  # Razorpay uses paise
    else:
        amount = 1000  # default 10.00 INR

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    context = {
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "order_id": payment["id"],
        "amount": amount,
        "currency": "INR",
    }
    return render(request, "razorpay_checkout.html", context)

@csrf_exempt
def razorpay_payment_success(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
            if cart_items.exists():
                # Calculate total
                total = sum(item.product.price * item.quantity for item in cart_items)
                # Create Order
                order = Order.objects.create(
                    user=request.user,
                    total=total,
                    status='pending'
                )
                # Create OrderItems
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                # Create Transaction
                Transaction.objects.create(
                    user=request.user,
                    order=order,
                    payment_id=request.POST.get('razorpay_payment_id', ''),
                    amount=total,
                    status='success'
                )
                # Clear cart
                cart_items.delete()
        else:
            request.session['cart'] = {}
        messages.success(request, "Payment successful! Your cart has been cleared and order placed.")
        return redirect('cart')
    return redirect('cart')

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