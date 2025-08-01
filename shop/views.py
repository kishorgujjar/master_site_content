from django.shortcuts import render, redirect, get_object_or_404
# from .models import Product
# from .models import Category
from django.contrib import messages
from .forms import ReviewForm
from .models import ReviewRating


# def shopView(request):
#     products = Product.objects.all().filter(is_available=True)
#     category = Category.objects.all()

#     CATID = request.GET.get('categories')  # from the URL ?categories=1
#     if CATID:
#         products = Product.objects.filter(category_id=CATID)  # ✅ correct field
#     else:
#         products = Product.objects.all()

#     context = {
#         'products': products,
#         'category': category,
#     }
#     return render(request, 'shop.html', context)

# def detailView(request, product_id):
#     product = Product.objects.get(id=product_id)
#     return render(request, 'product_detail.html', {'single_product': product})

# def add_to_cart(request, product_id):
#     # your add to cart logic here
#     return redirect('cart')  # or redirect back to product list

# def submit_review(request, product_id):
#     url = request.META.get('HTTP_REFERER')
#     if request.method == 'POST':
#         try:
#             reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
#             form = ReviewForm(request.POST, instance=reviews)
#             form.save()
#             messages.success(request, 'Thank you! Your review has been updated.')
#             return redirect()
#         except ReviewRating.DoesNotExist:
#             form = ReviewForm(request.POST)
#             if form.is_valid():
#                 data = ReviewRating()
#                 data.subject = form.cleaned_data['subject']
#                 data.rating = form.cleaned_data['rating'] 
#                 data.review = form.cleaned_data['review']
#                 data.ip = request.META.get('REMOTE_ADDR')
#                 data.product_id = product_id
#                 data.user_id = request.user.id
#                 data.save()
#                 messages.success(request, 'Thank you! Your review has been submited.')
#                 return redirect(url) 

#         return redirect(url) 


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


