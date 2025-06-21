from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Station
from django.forms import DateInput


class Searchform(forms.Form):
    origin=forms.ModelChoiceField(queryset=Station.objects.all(),required=True,label='Origin')
    destination = forms.ModelChoiceField(queryset=Station.objects.all(),required=True,label='Destination')
    date= forms.DateField(widget=DateInput(attrs={'type': 'date'}),required=True,input_formats=['%Y-%m-%d'],  # Format to expect from browser
        help_text="Select a date")



class Bookingform(forms.Form):
    name=forms.CharField(max_length=50)
    email=forms.EmailField()


