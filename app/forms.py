# forms.py
import os

from django import forms

from .models import Book, Author


class CreateBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'authors']

    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )


class SyllabusForm(forms.Form):
    direction_of_study = forms.CharField(max_length=128, required=True)
    university = forms.CharField(max_length=128, required=True)
    year = forms.IntegerField(min_value=1900, required=True)
    excel_file = forms.FileField(required=True)

    @property
    def template_name(self):
        return 'syllabus.html'

    def clean_excel_file(self):
        excel_file = self.cleaned_data.get('excel_file')
        if excel_file:
            # Проверяем расширение файла
            ext = os.path.splitext(excel_file.name)[1]
            if not ext.lower() == '.xlsx':
                raise forms.ValidationError('Only .xlsx files are allowed.')

        return excel_file


class BookFilterForm(forms.Form):
    title = forms.CharField(required=False, label='Название книги')
    author = forms.CharField(required=False, label='Имя автора')
