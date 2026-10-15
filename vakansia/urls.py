from django.urls import path

from . import views

app_name = 'vakansia'

urlpatterns = [
    path('', views.vacancy_list, name='vacancy_list'),
    path('vacancies/add/', views.vacancy_create, name='vacancy_create'),
    path('vacancies/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancies/<int:pk>/edit/', views.vacancy_update, name='vacancy_update'),
    path('vacancies/<int:pk>/delete/', views.vacancy_delete, name='vacancy_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
