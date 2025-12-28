from django import forms
from .models import Restaurant, MenuItem
from django.contrib.auth.forms import AuthenticationForm

# ──────────────── Restaurant & Menu Forms ────────────────
class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'restaurant_type', 'location', 'image']

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'price', 'image', 'is_available']

# ──────────────── Owner Login Form ────────────────
class OwnerLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'})
    )
