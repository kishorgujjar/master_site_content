from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q
from django.core.mail import send_mail, BadHeaderError
from smtplib import SMTPException
from django.contrib import messages
from shop.models import Product, ReviewRating
from accounts.models import Contact
from category.models import Category
from carts.models import Cart, CartItem
from orders.models import OrderProduct
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.contrib.auth.decorators import login_required

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def homeView(request):
    products = Product.objects.all().filter(is_available=True)
    category = Category.objects.all()

    CATID = request.GET.get('categories')  # from the URL ?categories=1
    if CATID:
        products = Product.objects.filter(category_id=CATID)  # correct field
    else:
        products = Product.objects.all()
    
    context = {
        'category' : category,
        'products' : products
    }
    return render(request, 'home.html', context)


def shopView(request):
    products = Product.objects.filter(is_available=True).order_by('id')
    category = Category.objects.all()

    # Category filter
    CATID = request.GET.get('categories')
    if CATID:
        products = products.filter(category_id=CATID)

    # Price filter
    selected_prices = request.GET.getlist('price')
    print(selected_prices, "Selected prices (raw)")

    if selected_prices:
        try:
            selected_prices_int = [int(price) for price in selected_prices]
            products = products.filter(price__in=selected_prices_int)
        except ValueError:
            pass  # Skip filter if invalid data

    # Pagination after all filters
    paginator = Paginator(products, 3)  # 3 products per page
    page_number = request.GET.get('page')
    pages_products = paginator.get_page(page_number)

    # Unique prices for filter sidebar
    prices = Product.objects.values_list('price', flat=True).distinct().order_by('price')

    context = {
        'category': category,
        'products': pages_products,  # Paginated filtered products
        'prices': prices,
        'selected_prices': selected_prices,
        'product_count': products.count(),
    }

    return render(request, 'shop.html', context)

def productDetailView(request, product_id):
    try:
        single_product = Product.objects.get(id=product_id)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product)
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try: 
            orderProduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist: 
            orderProduct = None
    else:
        orderProduct = None
    

    # get product reviews

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
 
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderProduct': orderProduct,
        'reviews': reviews,
    }
    return render(request, 'product_detail.html', context)


def contactView(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        print(message)
        contact = Contact(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        subject = subject
        message = message
        email_from = settings.EMAIL_HOST_USER
        # try:
        send_mail(
            subject,
            message,
            email_from,  # from
            ['kishorgujjar143@gmail.com'],  # to
            fail_silently=False,
        )
        contact.save()
    # except (BadHeaderError, SMTPException) as e:
        # print(f"Mail server error: {e}")
        messages.error(request, "Sorry Kishor Gujjar, it seems that our mail server is not responding. Please try again later.")
        return redirect('home')

    return render(request, 'contact.html')  # your form HTML page

def cartView(request):
    return render(request, 'cart.html')

@login_required(login_url='login')
def checkoutView(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        grand_total = total + tax

    except Cart.DoesNotExist:
        cart_items = []

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'tax': tax,
    }

    return render(request, 'checkout.html', context)


def searchView(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'shop.html', context)