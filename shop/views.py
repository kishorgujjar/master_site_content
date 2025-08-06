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
from django.core.paginator import Paginator
from .models import Product, Category, Variation

# def shopView(request):
#     products = Product.objects.filter(is_available=True).order_by('id')
#     category = Category.objects.all()

#     # Category filter
#     CATID = request.GET.get('categories')
#     if CATID:
#         products = products.filter(category_id=CATID)

#     # Price filter
#     selected_prices = request.GET.getlist('price')
#     if selected_prices:
#         try:
#             selected_prices_int = [int(price) for price in selected_prices]
#             products = products.filter(price__in=selected_prices_int)
#         except ValueError:
#             pass

#     # Size filter
#     selected_sizes = request.GET.getlist('size')
#     if selected_sizes:
#         products = products.filter(
#             id__in=Variation.objects.filter(variation_category='size', variation_value__in=selected_sizes)
#             .values_list('product_id', flat=True)
#         )

#     # Color filter
#     selected_colors = request.GET.getlist('color')
#     if selected_colors:
#         products = products.filter(
#             id__in=Variation.objects.filter(variation_category='color', variation_value__in=selected_colors)
#             .values_list('product_id', flat=True)
#         )

#     # Pagination
#     paginator = Paginator(products, 6)
#     page_number = request.GET.get('page')
#     pages_products = paginator.get_page(page_number)

#     # For filter sidebar
#     prices = Product.objects.values_list('price', flat=True).distinct().order_by('price')
#     sizes = Variation.objects.filter(variation_category='size').values_list('variation_value', flat=True).distinct()
#     colors = Variation.objects.filter(variation_category='color').values_list('variation_value', flat=True).distinct()

#     context = {
#         'category': category,
#         'products': pages_products,
#         'prices': prices,
#         'sizes': sizes,
#         'colors': colors,
#         'selected_prices': selected_prices,
#         'selected_sizes': selected_sizes,
#         'selected_colors': selected_colors,
#         'product_count': products.count(),
#     }

#     return render(request, 'shop.html', context)

from django.core.paginator import Paginator
from django.db.models import Avg
from .models import Product, Variation, Category

def shopView(request):
    sort = request.GET.get('sort', 'latest')

    # Base queryset: include rating annotation
    products = Product.objects.filter(is_available=True).annotate(average_rating=Avg('reviews__rating'))
    category = Category.objects.all()

    # Category filter
    CATID = request.GET.get('categories')
    if CATID:
        products = products.filter(category_id=CATID)

    # Price filter
    selected_prices = request.GET.getlist('price')
    if selected_prices:
        try:
            selected_prices_int = [int(price) for price in selected_prices]
            products = products.filter(price__in=selected_prices_int)
        except ValueError:
            pass

    # Size filter
    selected_sizes = request.GET.getlist('size')
    if selected_sizes:
        products = products.filter(
            id__in=Variation.objects.filter(variation_category='size', variation_value__in=selected_sizes)
            .values_list('product_id', flat=True)
        )

    # Color filter
    selected_colors = request.GET.getlist('color')
    if selected_colors:
        products = products.filter(
            id__in=Variation.objects.filter(variation_category='color', variation_value__in=selected_colors)
            .values_list('product_id', flat=True)
        )

    # Sort logic
    if sort == 'popularity':
        products = products.order_by('-views')  # Ensure 'views' field exists on Product
    elif sort == 'rating':
        products = products.order_by('-average_rating')
    else:
        products = products.order_by('-created_date')  # Default: latest

    # Pagination
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    pages_products = paginator.get_page(page_number)

    # For sidebar filters
    prices = Product.objects.values_list('price', flat=True).distinct().order_by('price')
    sizes = Variation.objects.filter(variation_category='size').values_list('variation_value', flat=True).distinct()
    colors = Variation.objects.filter(variation_category='color').values_list('variation_value', flat=True).distinct()

    context = {
        'category': category,
        'products': pages_products,
        'prices': prices,
        'sizes': sizes,
        'colors': colors,
        'selected_prices': selected_prices,
        'selected_sizes': selected_sizes,
        'selected_colors': selected_colors,
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


def searchView(request):
    keyword = request.GET.get('keyword', '').strip()
    products = Product.objects.none()
    product_count = 0
    error_message = ""

    try:
        products = Product.objects.order_by('-created_date')

        if keyword:
            words = keyword.split()
            query = Q()
            for word in words:
                query &= Q(product_name__icontains=word) | Q(description__icontains=word)

            products = products.filter(query)

        product_count = products.count()

    except Exception:
        messages.error("An error occurred while searching. Please try again later.")
        products = Product.objects.none()
        product_count = 0

    context = {
        'products': products,
        'product_count': product_count,
        'error_message': error_message,
    }
    return render(request, 'shop.html', context)



# Search Product by Name
def searchByNameView(request):
    keyword = request.GET.get('name_keyword', '').strip()
    products = Product.objects.none()
    product_count = 0
    error_message = ""

    try:
        products = Product.objects.order_by('-created_date')

        if keyword:
            words = keyword.split()
            for word in words:
                products = products.filter(product_name__icontains=word)

        product_count = products.count()

    except Exception:
        messages.error(request, "An error occurred while searching. Please try again later.")
        products = Product.objects.none()
        product_count = 0

    context = {
        'products': products,
        'product_count': product_count,
        'error_message': error_message,
    }
    return render(request, 'shop.html', context)


def productShortByView(request):
    sort = request.GET.get('sort', 'latest')
    products = Product.objects.all()

    if sort == 'popularity':
        products = products.order_by('-views')  # adjust as per your model
    elif sort == 'rating':
        products = products.order_by('-rating')  # adjust as per your model
    else:
        products = products.order_by('-created_date')  # default = latest

    context = {
        'products': products,
        'product_count': products.count(),
    }
    return render(request, 'shop.html', context)
