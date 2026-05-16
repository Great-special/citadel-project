from django import forms
from django.forms import formset_factory
from .models import CourseRegistration


class CourseRegistrationForm(forms.ModelForm):
    class Meta:
        model = CourseRegistration
        exclude = 'course',  # Exclude course field to be set programmatically
        widgets = {
            'session': forms.TextInput(attrs={'placeholder': 'Select a session'}),
            'name': forms.TextInput(attrs={'placeholder': 'Name*'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email*'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Designation/Position'}),
            'company': forms.TextInput(attrs={'placeholder': 'Company'}),
            'address': forms.TextInput(attrs={'placeholder': 'Address*'}),
            'city': forms.TextInput(attrs={'placeholder': 'City*'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country*'}),
            'telephone': forms.TextInput(attrs={'placeholder': 'Telephone'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Mobile*'}),
            'fax': forms.TextInput(attrs={'placeholder': 'Fax'}),
        }
