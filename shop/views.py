from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ReviewForm
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.core.mail import send_mail, BadHeaderError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from smtplib import SMTPException
from .models import Product, ReviewRating, ProductGallery
from accounts.models import Contact
from category.models import Category
from carts.models import Cart, CartItem
from orders.models import OrderProduct, Order
from django.contrib.auth.decorators import login_required
from carts.views import _cart_id


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
    paginator = Paginator(products, 6)  # 3 products per page
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

    # product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
 
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderProduct': orderProduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'product_detail.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')  # Redirect back to previous page

    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user=request.user, product_id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = ReviewRating()
                review.subject = form.cleaned_data['subject']
                review.review = form.cleaned_data['review']
                review.rating = form.cleaned_data['rating']
                review.ip = request.META.get('REMOTE_ADDR')
                review.product_id = product_id
                review.user = request.user
                review.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)


