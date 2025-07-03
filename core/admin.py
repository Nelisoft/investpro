from django.contrib import admin
from .models import Deposit, DepositMethod,WithdrawalMethod, WithdrawalRequest

@admin.register(DepositMethod)
class DepositMethodAdmin(admin.ModelAdmin):
    list_display = ('coin', 'network', 'wallet_address', 'coin_logo')
    search_fields = ('coin', 'wallet_address', 'network')

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'method', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'method__coin')
    readonly_fields = ('created_at', 'reviewed_at')



admin.site.register(WithdrawalMethod)
admin.site.register(WithdrawalRequest)
