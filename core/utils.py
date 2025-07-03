from decimal import Decimal
from django.db.models import Sum
from .models import Deposit, WithdrawalRequest


def get_user_balance(user):
    total_deposits = Deposit.objects.filter(user=user, status='approved').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_withdrawals = WithdrawalRequest.objects.filter(user=user, status='Approved').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    return total_deposits - total_withdrawals
