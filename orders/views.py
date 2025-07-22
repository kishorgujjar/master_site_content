from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from carts.models import Cart, CartItem
import datetime
from .forms import OrderForm
from carts.models import Cart, CartItem
from .models import Order, Payment, OrderProduct
import json
import random
from django.http import HttpResponse


import json
import random
from django.http import JsonResponse
from orders.models import Order, Payment, OrderProduct
from carts.models import CartItem

import json
from django.http import JsonResponse
from orders.models import Order, Payment, OrderProduct
from carts.models import CartItem

def paymentsView(request):
    if request.method == "POST":
        body = json.loads(request.body)

        # Static fallback if frontend sends no data
        orderID = body.get('orderID', 'STATICORDER123')
        transID = body.get('transID', 'TXNSTATIC123456')
        payment_method = body.get('payment_method', 'Cash on Delivery')
        status = body.get('status', 'Completed')

        try:
            # Get the order with static orderID
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=orderID)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found.'}, status=404)

        # Save Payment (static values)
        payment = Payment.objects.create(
            user=request.user,
            payment_id=transID,
            payment_method=payment_method,
            amount_paid=order.order_total,
            status=status,
        )

        # Update Order
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move Cart Items to OrderProduct (static)
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            OrderProduct.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True,
            )
            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()

        # Clear Cart
        cart_items.delete()

        # Return static response
        return JsonResponse({
            'order_number': order.order_number,
            'transaction_id': payment.payment_id,
            'message': 'Order confirmed with static data.'
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def placeOrderView(request, total=0, quantity=0):
    current_user = request.user

    # Check if cart has items
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        messages.error(request, "Your cart is empty.")
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():

            data = Order()
            
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.pin_code = form.cleaned_data['pin_code']
            data.order_note = form.cleaned_data.get('order_note', '')
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))

            # Generate order number
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            messages.success(request, "Your order has been placed successfully.")
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'payments.html', context)
    else:
        return redirect('checkout')