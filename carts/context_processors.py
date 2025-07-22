from .models import Cart, CartItem
from .views import _cart_id

def cart_counter(request):
    cart_count = 0

    if 'admin' in request.path:
        return {}

    try:
        if request.user.is_authenticated:
            # Logged-in user's cart items
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            # Guest user's cart items (session-based)
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            cart_count += cart_item.quantity

    except Cart.DoesNotExist:
        cart_count = 0

    return dict(cart_counter=cart_count)
