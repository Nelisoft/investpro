from django import forms
from .models import CustomUser
from django_countries.widgets import CountrySelectWidget

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'country', 'profile_picture']




class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'country']
        widgets = {
            'country': CountrySelectWidget(),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()
        return user



class ProfileForm(forms.ModelForm):
    referral_code = forms.CharField(max_length=10, required=False, help_text="Referral code (optional)")
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'country','referral_code']
