from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import Q
from django.core.mail import send_mail, BadHeaderError
from smtplib import SMTPException
from django.contrib import messages
from shop.models import Product, ReviewRating, ProductGallery
from accounts.models import Contact
from category.models import Category
from carts.models import Cart, CartItem
from orders.models import OrderProduct, Order
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.contrib.auth.decorators import login_required



def homeView(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    category = Category.objects.all()

    CATID = request.GET.get('categories')  # from the URL ?categories=1
    if CATID:
        products = Product.objects.filter(category_id=CATID)  # correct field
    else:
        products = Product.objects.all()
    
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    
    context = {
        'category' : category,
        'products' : products,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)


def contactView(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        contact = Contact(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                ['kishorgujjar143@gmail.com'],
                fail_silently=False,
            )
            contact.save()
            messages.success(request, f"Thank you, {name}. Your message has been sent successfully!")
        except (BadHeaderError, SMTPException) as e:
            print(f"Mail server error: {e}")
            messages.error(
                request,
                f"Sorry {name}, it seems that our mail server is not responding. Please try again later."
            )
        return redirect('home')

    return render(request, 'contact.html')


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