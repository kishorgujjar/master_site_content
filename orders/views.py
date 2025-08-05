from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from carts.models import Cart, CartItem
from django.http import JsonResponse
import datetime
from .forms import OrderForm
from carts.models import Cart, CartItem
from .models import Order, Payment, OrderProduct
import json
import random
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import json
import random
from django.http import JsonResponse, HttpResponseBadRequest
from orders.models import Order, Payment, OrderProduct
from carts.models import CartItem
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
import razorpay


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def placeOrderView(request, total=0, quantity=0):
    current_user = request.user

    # Check if cart has items
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        messages.error(request, "Your cart is empty.")
        return redirect('shop')

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



@csrf_exempt
def paymentsView(request):
    if request.method == "GET":
        order = Order.objects.filter(user=request.user, is_ordered=False).last()
        if not order:
            return JsonResponse({'error': 'No pending order'}, status=404)

        amount_paise = int(order.order_total * 100)

        razorpay_order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1,
            "receipt": f"receipt_{order.order_number}"
        })

        # ✅ Save razorpay_order_id to the order
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        return JsonResponse({
            'razorpay_order_id': razorpay_order['id'],
            'amount': amount_paise,
            'currency': "INR",
            'order_number': order.order_number,
            'key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_callback_url': settings.RAZORPAY_CALLBACK_URL,
        })

    
@csrf_exempt
def paymentSuccessView(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        razorpay_order_id = body.get('razorpay_order_id')
        razorpay_payment_id = body.get('razorpay_payment_id')
        razorpay_signature = body.get('razorpay_signature')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({'error': 'Missing payment details'}, status=400)

        try:
            # Signature verification
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)
        except Exception:
            return JsonResponse({'error': 'Signature verification failed'}, status=400)

        try:
            order = Order.objects.get(user=request.user, razorpay_order_id=razorpay_order_id, is_ordered=False)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        # Create Payment
        payment = Payment.objects.create(
            user=request.user,
            payment_method="Razorpay",
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            amount_paid=order.order_total,
            status="Completed",
            is_paid=True,  # ✅ Set this explicitly
        )

        # Finalize Order
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move items to OrderProduct
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            order_product = OrderProduct.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True,
            )
            order_product.variations.set(item.variation.all())
            item.product.stock -= item.quantity
            item.product.save()
        # cart_items.delete()

        # Send confirmation email
        subject = 'Thank you for your order!'
        message = render_to_string('order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        EmailMessage(subject, message, to=[to_email]).send()

        return JsonResponse({
            'success': True,
            'message': 'Payment successful',
            'order_number': order.order_number,
            'transaction_id': payment.razorpay_payment_id,
        })

    elif request.method == "GET":
        order_number = request.GET.get('order_number')
        transaction_id = request.GET.get('payment_id')

        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
        except Order.DoesNotExist:
            return HttpResponse("Invalid order.", status=404)

        payment = order.payment
        ordered_products = OrderProduct.objects.filter(order=order)
        sub_total = sum(item.product_price * item.quantity for item in ordered_products)

        return render(request, 'payment_success.html', {
            'order': order,
            'payment': payment,
            'ordered_products': ordered_products,
            'sub_total': sub_total,
            'order_number': order.order_number,
            'order_date': order.created_at.strftime('%d %B %Y, %I:%M %p'),
            'transaction_id': payment.razorpay_payment_id if payment else transaction_id,
            'payment_method': payment.payment_method if payment else 'N/A',
            'payment_status': payment.status if payment else 'Pending',
            'is_paid': payment.status.lower() == "completed" if payment else False,
        })


    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
