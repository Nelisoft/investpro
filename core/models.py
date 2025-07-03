from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class DepositMethod(models.Model):
    coin = models.CharField(max_length=50)  # e.g. USDT, BTC
    wallet_address = models.CharField(max_length=255)
    network = models.CharField(max_length=50, blank=True, null=True)  # e.g. TRC20, ERC20
    coin_logo = models.ImageField(upload_to='coin_logos/', blank=True, null=True)

    def __str__(self):
        network_display = f" ({self.network})" if self.network else ""
        return f"{self.coin}{network_display} - {self.wallet_address[:15]}..."


class Deposit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    method = models.ForeignKey(DepositMethod, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    payment_proof = models.ImageField(upload_to='payment_proofs/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.method.coin} - {self.amount} - {self.status}"




# models.py

class WithdrawalMethod(models.Model):
    coin_name = models.CharField(max_length=50)
    network = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='coin_logos/', null=True, blank=True)  # NEW

    def __str__(self):
        return f"{self.coin_name} ({self.logo})"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    method = models.ForeignKey(WithdrawalMethod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    user_wallet_address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.method.coin_name}"
