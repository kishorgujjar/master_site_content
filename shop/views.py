from django.shortcuts import render, redirect, get_object_or_404
# from .models import Product
# from .models import Category



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
