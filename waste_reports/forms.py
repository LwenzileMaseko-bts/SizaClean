from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import WasteReport


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]


class WasteReportForm(forms.ModelForm):
    class Meta:
        model = WasteReport
        fields = [
            'problem_type',
            'description',
            'location',
            'latitude',
            'longitude',
            'photo',
        ]

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Describe the waste problem...'
            }),

            'location': forms.TextInput(attrs={
                'placeholder': 'Enter the location of the problem'
            }),

            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }