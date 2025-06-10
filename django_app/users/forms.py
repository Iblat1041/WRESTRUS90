from django import forms
from .models import ChildRegistration

class ChildRegistrationForm(forms.ModelForm):
    class Meta:
        model = ChildRegistration
        fields = ['child_name', 'age', 'parent_contact']