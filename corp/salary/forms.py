from django import forms
from .models import Payments, Salary


class PayslipForm(forms.ModelForm):
    class Meta:
        model = Payments
        fields = ()


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ()
