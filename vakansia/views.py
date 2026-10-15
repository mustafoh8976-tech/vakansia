from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import CategoryForm, RequestForm, VacancyForm
from .models import Category, Request, Vacancy


def vacancy_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    vacancies = Vacancy.objects.select_related('category')

    if query:
        vacancies = vacancies.filter(
            Q(title__icontains=query)
            | Q(company__icontains=query)
            | Q(location__icontains=query)
            | Q(description__icontains=query)
        )
    if category_id.isdigit():
        vacancies = vacancies.filter(category_id=int(category_id))

    page_obj = Paginator(vacancies, 8).get_page(request.GET.get('page'))
    return render(
        request,
        'vakansia/vacancy_list.html',
        {
            'page_obj': page_obj,
            'categories': Category.objects.annotate(vacancy_count=Count('vacancies')),
            'query': query,
            'selected_category': category_id,
            'total_count': vacancies.count(),
        },
    )


def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy.objects.select_related('category'), pk=pk)
    form = RequestForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        application = Request.objects.filter(
            email__iexact=form.cleaned_data['email'],
        ).first()
        if application is None:
            application = form.save()
        application.vacancies.add(vacancy)
        messages.success(request, 'Ваш отклик отправлен работодателю.')
        return redirect('vakansia:vacancy_detail', pk=vacancy.pk)

    return render(
        request,
        'vakansia/vacancy_detail.html',
        {'vacancy': vacancy, 'form': form},
    )


def vacancy_create(request):
    form = VacancyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        vacancy = form.save()
        messages.success(request, 'Вакансия опубликована.')
        return redirect('vakansia:vacancy_detail', pk=vacancy.pk)
    return render(
        request,
        'vakansia/form.html',
        {
            'form': form,
            'title': 'Новая вакансия',
            'back_url': 'vakansia:vacancy_list',
            'cancel_url': 'vakansia:vacancy_list',
            'vacancy_form': True,
            'has_categories': Category.objects.exists(),
        },
    )


def vacancy_update(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    form = VacancyForm(request.POST or None, instance=vacancy)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Изменения сохранены.')
        return redirect('vakansia:vacancy_detail', pk=vacancy.pk)
    return render(
        request,
        'vakansia/form.html',
        {
            'form': form,
            'title': 'Редактировать вакансию',
            'back_url': 'vakansia:vacancy_detail',
            'back_args': (vacancy.pk,),
            'cancel_url': 'vakansia:vacancy_detail',
            'cancel_args': (vacancy.pk,),
            'vacancy_form': True,
            'has_categories': True,
        },
    )


def vacancy_delete(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    if request.method == 'POST':
        vacancy.delete()
        messages.success(request, 'Вакансия удалена.')
        return redirect('vakansia:vacancy_list')
    return render(
        request,
        'vakansia/confirm_delete.html',
        {
            'object': vacancy,
            'title': 'Удалить вакансию',
            'cancel_url': 'vakansia:vacancy_detail',
            'cancel_args': (vacancy.pk,),
        },
    )


def category_list(request):
    categories = Category.objects.annotate(vacancy_count=Count('vacancies'))
    return render(request, 'vakansia/category_list.html', {'categories': categories})


def category_create(request):
    next_url = request.POST.get('next') or request.GET.get('next', '')
    if next_url and not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ''

    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Категория добавлена.')
        if next_url:
            return redirect(next_url)
        return redirect('vakansia:category_list')
    return render(
        request,
        'vakansia/form.html',
        {
            'form': form,
            'title': 'Новая категория',
            'back_url': 'vakansia:category_list',
            'cancel_url': 'vakansia:category_list',
            'next_url': next_url,
        },
    )


def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Категория обновлена.')
        return redirect('vakansia:category_list')
    return render(
        request,
        'vakansia/form.html',
        {
            'form': form,
            'title': 'Редактировать категорию',
            'back_url': 'vakansia:category_list',
            'cancel_url': 'vakansia:category_list',
        },
    )


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        if category.vacancies.exists():
            messages.error(
                request,
                'Нельзя удалить категорию, пока к ней привязаны вакансии.',
            )
        else:
            category.delete()
            messages.success(request, 'Категория удалена.')
        return redirect('vakansia:category_list')
    return render(
        request,
        'vakansia/confirm_delete.html',
        {
            'object': category,
            'title': 'Удалить категорию',
            'cancel_url': 'vakansia:category_list',
        },
    )
