from django import forms
from .models import Order, Price


class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ()
