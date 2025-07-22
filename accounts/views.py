from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .forms import UserRegistrationForm
from django.contrib import messages, auth
from .models import Account
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests



def registerView(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            email=form.cleaned_data['email']
            phone_number=form.cleaned_data['phone_number']
            password=form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name=first_name, 
                last_name=last_name, 
                username=username, 
                email=email, 
                password=password, 
                phone_number=phone_number
            )
            user.phone_number = phone_number
            user.save()

            current_site = get_current_site(request)
            subject = 'Please Activate your account'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = EmailMessage(subject, message, to=[user.email])
            to_email.send()
            return redirect('/login/?command=verification&email=' + email)
            # return redirect(f'/registration/login/?command=verification&email={email}')
            # messages.success(request, 'Registration successful!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'registration/register.html', context)


def loginView(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items_session = CartItem.objects.filter(cart=cart)

                if cart_items_session.exists():
                    product_variation = []
                    for item in cart_items_session:
                        variations = list(item.variation.all().order_by('id'))  # Order variations by ID for consistency
                        product_variation.append(variations)

                    cart_items_user = CartItem.objects.filter(user=user)
                    existing_variations = []
                    item_ids = []

                    for item in cart_items_user:
                        variations = list(item.variation.all().order_by('id'))
                        existing_variations.append(variations)
                        item_ids.append(item.id)

                    for pr in product_variation:
                        if pr in existing_variations:
                            index = existing_variations.index(pr)
                            item_id = item_ids[index]
                            item = CartItem.objects.get(id=item_id)
                            # Increase quantity since same variation exists
                            item.quantity += 1
                            item.save()
                        else:
                            # Assign session cart item to logged-in user
                            for item in cart_items_session:
                                item.user = user
                                item.save()
                else:
                    # No session cart items to transfer
                    pass

            except Cart.DoesNotExist:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # print("query->", query)
                params = dict(x.split('=') for x in query.split('&')) 
                # print("param - >", params)
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

    return render(request, 'registration/login.html')

@login_required(login_url = 'login')
def logoutView(request):
    auth.logout(request)
    messages.success(request, 'You are Logged Out')
    return redirect('login')

def activateView(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalide activation link')
        return redirect('register')
    
def forgotPasswordView(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            # reset your password
            current_site = get_current_site(request)
            subject = 'Reset Your Password.'
            message = render_to_string('registration/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            to_email = EmailMessage(subject, message, to=[user.email])
            to_email.send()

            messages.success(request, 'Password reset link send to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')

    return render(request, 'registration/forgotPassword.html')

def resetpasswordValidateView(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password!')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expire')
        return redirect('login')
    
def resetPasswordView(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_passowrd = request.POST['confirm_password']

        if password == confirm_passowrd:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match')
            return redirect('resetPassword')
    return render(request, 'registration/resetPassword.html')

def dashboardView(request):
    return render(request, 'registration/dashboard.html')
