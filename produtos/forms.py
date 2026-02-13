from django import forms
from .models import Venda

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['quantidade'] # so pedimos quantidade, o produto vem do URL
        widgets = {
            'quantidade': forms.NumberInput(attrs={'min':1})
        }
