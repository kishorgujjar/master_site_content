from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.contrib import messages

def cart(request):
    return render(request, 'cart.html')

# Get or create session cart ID
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_to_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # if the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()

        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, user=current_user)

            existing_variations = []
            item_ids = []

            for item in cart_items:
                variations = list(item.variation.all().order_by('id'))  # Order by id to avoid list comparison issues
                existing_variations.append(list(variations))  # Make sure it's a list
                item_ids.append(item.id)

            matched = False
            for i, existing_variation in enumerate(existing_variations):
                # Compare variations as sets to ignore order
                if set(existing_variation) == set(product_variation):
                    item_id = item_ids[i]
                    item = CartItem.objects.get(id=item_id)
                    item.quantity += 1
                    item.save()
                    matched = True
                    break

            if not matched:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if product_variation:
                    item.variation.set(product_variation)
                item.save()

        else:
            item = CartItem.objects.create(product=product, quantity=1, user=current_user)
            if product_variation:
                item.variation.set(product_variation)
            item.save()

        return redirect('cart')
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, cart=cart)

            existing_variations = []
            item_ids = []

            for item in cart_items:
                variations = list(item.variation.all().order_by('id'))  # Order by id to avoid list comparison issues
                existing_variations.append(list(variations))  # Make sure it's a list
                item_ids.append(item.id)

            matched = False
            for i, existing_variation in enumerate(existing_variations):
                # Compare variations as sets to ignore order
                if set(existing_variation) == set(product_variation):
                    item_id = item_ids[i]
                    item = CartItem.objects.get(id=item_id)
                    item.quantity += 1
                    item.save()
                    matched = True
                    break

            if not matched:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if product_variation:
                    item.variation.set(product_variation)
                item.save()

        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if product_variation:
                item.variation.set(product_variation)
            item.save()

        return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass  # No cart yet

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)


def remove_from_cart(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')



# Create your views here.
