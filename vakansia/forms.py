from django import forms

from .models import Category, Request, Vacancy


class VacancyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Выберите категорию'

    class Meta:
        model = Vacancy
        fields = ('title', 'company', 'category', 'location', 'salary', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('name', 'email', 'phone', 'message')
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
