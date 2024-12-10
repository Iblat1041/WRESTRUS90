from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.deconstruct import deconstructible

from .models import Competition


class AddPostForm(forms.ModelForm):

    class Meta:
        model = Competition
        fields = [
            'title', 'slug', 'content', 'cat', 'photo', 'is_published',]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        }
        labels = {'slug': 'URL'}

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 100:
            raise ValidationError("Длина превышает 100 символов")

        return title


class UploadFileForm(forms.Form):
    file = forms.ImageField(label="Файл")
