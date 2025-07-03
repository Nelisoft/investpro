
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DepositForm
from .models import DepositMethod,Deposit,WithdrawalMethod, WithdrawalRequest
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Sum
from .forms import WithdrawalRequestForm
from .utils import get_user_balance  # from our earlier discussion

from django.core.paginator import Paginator

def Home(request):
    return render(request, 'core/frontend/index.html')

@login_required
def Dashboard(request):
    user = request.user

    # Get user balance (sum of approved deposits, minus withdrawals, etc.)
    balance = get_user_balance(user)

    # Fetch deposits and withdrawals for the user
    deposits = Deposit.objects.filter(user=user).select_related('method')
    withdrawals = WithdrawalRequest.objects.filter(user=user).select_related('method')

    # Combine and normalize transactions for dashboard summary
    transactions = []

    for d in deposits:
        transactions.append({
            'type': 'Deposit',
            'amount': d.amount,
            'coin': d.method.coin,
            'network': d.method.network,
            'status': d.status,
            'date': d.created_at,
            
            'wallet': None,
        })

    for w in withdrawals:
        transactions.append({
            'type': 'Withdrawal',
            'amount': w.amount,
            'coin': w.method.coin_name,
            'network': w.method.network,
            'status': w.status,
            'date': w.requested_at,
            
            'wallet': w.user_wallet_address,
        })

    # Sort transactions by date descending
    transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)

    # Paginate transactions, showing e.g. 5 on dashboard
    paginator = Paginator(transactions, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'balance': balance,
        'transactions': page_obj,
    }
    return render(request, 'core/dashboard/index.html', context)

@login_required
def deposit_view(request):
    if request.method == 'POST':
        form = DepositForm(request.POST, request.FILES)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.save()

            # Send deposit confirmation email
            subject = 'Deposit Received - HYIP Investment Platform'
            context = {
                'user': request.user,
                'deposit': deposit,
            }
            message = render_to_string('core/emails/deposit_confirmation.html', context)
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)

            messages.success(request, 'Deposit submitted successfully. Check your email for confirmation.')
            return redirect('dashboard')  # or any page you want
    else:
        form = DepositForm()

    return render(request, 'core/dashboard/deposit.html', {'form': form})



@login_required
def withdraw_view(request):
    user = request.user
    methods = WithdrawalMethod.objects.all()
    balance = get_user_balance(user)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        method_id = request.POST.get('method')
        wallet_address = request.POST.get('user_wallet_address')

        if not amount or not method_id or not wallet_address:
            messages.error(request, "All fields are required.")
            return redirect('withdraw')

        try:
            amount = float(amount)
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect('withdraw')

        if amount > balance:
            messages.error(request, "Insufficient balance to make this withdrawal.")
            return redirect('withdraw')

        try:
            method = WithdrawalMethod.objects.get(id=method_id)
        except WithdrawalMethod.DoesNotExist:
            messages.error(request, "Selected method is invalid.")
            return redirect('withdraw')

        withdrawal = WithdrawalRequest.objects.create(
            user=user,
            amount=amount,
            method=method,
            user_wallet_address=wallet_address,
            status='Pending',
        )

        # Send email
        context = {'user': user, 'withdrawal': withdrawal}
        message = render_to_string('core/emails/withdrawal_notification.html', context)
        email = EmailMessage(
            subject='Withdrawal Request Received - HYIP Investment Platform',
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)

        messages.success(request, "Withdrawal request submitted. A confirmation email has been sent.")
        return redirect('dashboard') 

    return render(request, 'core/dashboard/withdraw.html', {
        'balance': balance,
        'methods': methods
    })



@login_required
def withdrawal_history_view(request):
    withdrawals = request.user.withdrawalrequest_set.order_by('-requested_at')
    return render(request, 'core/dashboard/withdrawal_history.html', {
        'withdrawals': withdrawals
    })



@login_required
def deposit_history_view(request):
    deposits = Deposit.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/dashboard/deposit_history.html', {'deposits': deposits})



@login_required
def transaction_history(request):
    user = request.user

    # Get deposits
    deposits = Deposit.objects.filter(user=user).select_related('method')
    deposit_list = [{
        'transaction_type': 'deposit',
        'amount': d.amount,
        'coin': d.method.coin,
        'network': d.method.network,
        'status': d.status,
        'date': d.created_at,
        'proof': d.proof,
        'wallet': None,
    } for d in deposits]

    # Get withdrawals
    withdrawals = Withdrawal.objects.filter(user=user).select_related('method')
    withdrawal_list = [{
        'transaction_type': 'withdrawal',
        'amount': w.amount,
        'coin': w.method.coin_name,
        'network': w.method.network,
        'status': w.status,
        'date': w.requested_at,
        'proof': None,
        'wallet': w.user_wallet_address,
    } for w in withdrawals]

    # Combine and sort by date (descending)
    transactions = sorted(deposit_list + withdrawal_list, key=lambda x: x['date'], reverse=True)

    return render(request, 'core/dashboard/transaction_history.html', {
        'transactions': transactions
    })

