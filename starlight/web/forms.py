from django import forms

from .models import Subscriber 

class WebForm(forms.ModelForm):

    class Meta:
        model = Subscriber 
        fields = ('product', 'email', 'first_name',)
