from django.contrib import admin

from .models import Category, Request, Vacancy


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'category', 'location', 'created_at')
    list_filter = ('category', 'location')
    search_fields = ('title', 'company', 'location', 'description')


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    filter_horizontal = ('vacancies',)
