# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import EmailVerificationToken
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.conf import settings
from .forms import ProfileUpdateForm,ProfileForm
from django_countries import countries
from core.utils import get_user_balance 





from .models import EmailVerificationToken, CustomUser
User = get_user_model()  # Use the custom user model here


def Register(request):
    if request.user.is_authenticated and request.user.id != 1:
        return redirect('dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        country = request.POST.get('country', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        

        # Basic validation
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if not country or country not in dict(countries).keys():
            messages.error(request, "Please select a valid country.")
            return redirect('register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        # You might want to check phone validity here (optional)

        new_user = CustomUser.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone=phone,
            country=country,
            password=password1,
            is_active=False
        )

        # Send Welcome Email
        welcome_html = render_to_string('emails/welcome_email.html', {
            'first_name': first_name,
            'last_name': last_name
        })
        welcome_email = EmailMessage(
            subject='Welcome to HYIP Investment Platform',
            body=welcome_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        welcome_email.content_subtype = 'html'
        welcome_email.send(fail_silently=False)

        # Create verification token
        token = EmailVerificationToken.objects.create(user=new_user)

        # Send Verification Email
        uid = urlsafe_base64_encode(force_bytes(new_user.pk))
        verification_link = request.build_absolute_uri(
            reverse('verify_email', kwargs={'uidb64': uid, 'token': token.token})
        )
        verification_html = render_to_string('emails/verification_email.html', {
            'first_name': first_name,
            'verification_link': verification_link
        })
        verification_email = EmailMessage(
            subject='Verify Your HYIP Account',
            body=verification_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        verification_email.content_subtype = 'html'
        verification_email.send(fail_silently=False)

        messages.success(request, 'Account created. Check your email to verify your account.')
        return redirect('resend_verification')

    return render(request, 'userauth/register.html', {'countries': countries})

def verify_email(request, uidb64, token):
    if request.user.is_authenticated and request.user.id != 1:
        return redirect('dashboard')
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        token_obj = EmailVerificationToken.objects.get(user=user)
    except (User.DoesNotExist, EmailVerificationToken.DoesNotExist):
        user = None

    if user and str(token_obj.token) == token:
        if token_obj.is_expired():
            token_obj.delete()
            messages.error(request, 'Verification link expired. Please register again.')
            return redirect('register')

        user.is_active = True
        user.save()
        token_obj.delete()
        messages.success(request, 'Email verified successfully. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('register')


def resend_verification_view(request):
    if request.user.is_authenticated and request.user.id != 1:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                messages.info(request, 'This account is already verified. Please log in.')
                return redirect('login')

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )

            verification_html = render_to_string('emails/verification_email.html', {
                'first_name': user.first_name,
                'verification_link': verification_link,
            })

            email_msg = EmailMessage(
                subject='Verify Your HYIP Account (Resend)',
                body=verification_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)

            request.session.pop('unverified_user_email', None)

            messages.success(request, 'Verification email has been resent. Please check your inbox.')
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    else:
        email = request.GET.get('email', '')
        context = {'email': email}
        return render(request, 'userauth/resend_verification.html', context)

    return render(request, 'userauth/resend_verification.html')


def Login(request):
    if request.user.is_authenticated and request.user.id != 1:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                request.session.pop('unverified_user_email', None)
                return redirect('dashboard')
            else:
                request.session['unverified_user_email'] = user.email
                messages.error(request, 'Please verify your email before logging in.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'userauth/login.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def password_reset_request(request):
    if request.user.is_authenticated and request.user.id != 1:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                f"/userauth/reset/{uid}/{token}/"
            )
            email_body = render_to_string('emails/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link
            })
            email_msg = EmailMessage(
                'Reset Your Password',
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email_msg.content_subtype = 'html'
            email_msg.send()

            messages.success(request, 'A reset link has been sent to your email.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No user with this email found.')

    return render(request, 'userauth/password_reset.html')


def password_reset_confirm_view(request, uidb64, token):
    if request.user.is_authenticated and request.user.id != 1:
        return redirect('dashboard')
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You can now log in.")
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'userauth/password_reset_confirm.html', {
            'form': form,
            'validlink': validlink
        })
    else:
        validlink = False
        return render(request, 'userauth/password_reset_confirm.html', {
            'validlink': validlink
        })


def password_reset_complete(request):
    if request.user.is_authenticated and request.user.id != 1:
        return redirect('dashboard')
    return render(request, 'userauth/password_reset_complete.html')


#




@login_required
def profile(request):
    user = request.user
    balance = get_user_balance(user)  # ✅ Get user current balance

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        country = request.POST.get('country', '').strip()

        # Optional checks for unique username/email
        if (
            request.user.username != username and
            request.user.__class__.objects.filter(username=username).exclude(pk=request.user.pk).exists()
        ):
            messages.error(request, 'Username already taken.')
        elif (
            request.user.email != email and
            request.user.__class__.objects.filter(email=email).exclude(pk=request.user.pk).exists()
        ):
            messages.error(request, 'Email already taken.')
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.phone = phone
            user.country = country
            user.save()

            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')

    return render(request, 'core/dashboard/profile.html', {
        'countries': list(countries),
        'balance': balance,  # ✅ Pass balance to template
    })
