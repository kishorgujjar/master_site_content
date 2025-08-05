from django.shortcuts import render, redirect, get_object_or_404
# from .models import Product
# from .models import Category
from django.contrib import messages
from .forms import ReviewForm
from .models import ReviewRating
from django.conf import settings
from .models import Product


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


