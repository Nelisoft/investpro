from django import forms
from .models import Deposit, DepositMethod
from .models import WithdrawalMethod,WithdrawalRequest
from decimal import Decimal


class DepositForm(forms.ModelForm):
    method = forms.ModelChoiceField(
        queryset=DepositMethod.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Deposit Method"
    )

    class Meta:
        model = Deposit
        fields = ['method', 'amount', 'payment_proof']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'payment_proof': forms.FileInput(attrs={'class': 'form-control'}),
        }






class WithdrawalRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'method', 'user_wallet_address']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset to all WithdrawalMethod objects so dropdown is populated
        self.fields['method'].queryset = WithdrawalMethod.objects.all()
        self.fields['user_wallet_address'].label = "Your Wallet Address"
        self.fields['amount'].widget.attrs.update({'step': 'any'})  # Allow decimals
