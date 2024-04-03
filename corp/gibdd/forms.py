from django import forms
from .models import Gibdd, CompanyPenalty


class GibddForm(forms.ModelForm):
    class Meta:
        model = Gibdd
        fields = ()


class CompanyPenaltyForm(forms.ModelForm):
    class Meta:
        model = CompanyPenalty
        fields = ()
