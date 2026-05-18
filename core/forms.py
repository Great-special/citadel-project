from django import forms
from django.forms import formset_factory
from .models import CourseRegistration


class CourseRegistrationForm(forms.ModelForm):
    class Meta:
        model = CourseRegistration
        exclude = 'course',  # Exclude course field to be set programmatically
        widgets = {
            'session': forms.TextInput(attrs={'placeholder': 'Select a session'}),
            'title': forms.Select(),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_class = 'reg-select' if isinstance(field.widget, forms.Select) else 'reg-input'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing} {css_class}'.strip()
            field.widget.attrs.setdefault('autocomplete', 'off')

        self.fields['session'].widget.attrs['placeholder'] = 'Preferred session or intake'
