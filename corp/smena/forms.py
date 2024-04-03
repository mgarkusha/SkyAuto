from django import forms
from .models import Smena, Run


class SmenaForm(forms.ModelForm):
    class Meta:
        model = Smena
        fields = ()


class RunForm(forms.ModelForm):
    class Meta:
        model = Run
        fields = ()
