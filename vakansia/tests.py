from django.test import TestCase

from django.urls import reverse

from .models import Category, Request, Vacancy


class VacancySiteTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='IT')
        self.vacancy = Vacancy.objects.create(
            category=self.category,
            title='Python-разработчик',
            company='Техно',
            location='Душанбе',
            salary='10 000 сомони',
            description='Разработка веб-приложений',
        )

    def test_search_matches_title_company_and_description(self):
        for term in ('Python', 'Техно', 'веб-приложений'):
            with self.subTest(term=term):
                response = self.client.get(reverse('vakansia:vacancy_list'), {'q': term})
                self.assertContains(response, self.vacancy.title)

        response = self.client.get(reverse('vakansia:vacancy_list'), {'q': 'учитель'})
        self.assertNotContains(response, self.vacancy.title)

    def test_each_page_loads_its_own_stylesheet_and_shared_base_css(self):
        pages = (
            (reverse('vakansia:vacancy_list'), 'vacancy_list.css'),
            (
                reverse('vakansia:vacancy_detail', args=(self.vacancy.pk,)),
                'vacancy_detail.css',
            ),
            (reverse('vakansia:vacancy_create'), 'form.css'),
            (
                reverse('vakansia:vacancy_delete', args=(self.vacancy.pk,)),
                'confirm_delete.css',
            ),
            (reverse('vakansia:category_list'), 'category_list.css'),
        )

        for url, stylesheet in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, '/static/css/base.css')
                self.assertContains(response, f'/static/css/{stylesheet}')
                self.assertNotContains(response, '/static/css/style.css')

    def test_category_filter_shows_only_matching_vacancies(self):
        other_category = Category.objects.create(name='Продажи')
        other_vacancy = Vacancy.objects.create(
            category=other_category,
            title='Менеджер',
            company='Магазин',
            description='Продажи',
        )

        response = self.client.get(
            reverse('vakansia:vacancy_list'),
            {'category': self.category.pk},
        )

        self.assertContains(response, self.vacancy.title)
        self.assertNotContains(response, other_vacancy.title)

    def test_vacancy_crud(self):
        create_url = reverse('vakansia:vacancy_create')
        create_page = self.client.get(create_url)
        self.assertContains(create_page, 'Выберите категорию')
        self.assertNotContains(create_page, 'Select an option')

        create_response = self.client.post(
            create_url,
            {
                'title': 'Дизайнер',
                'company': 'Студия',
                'category': self.category.pk,
                'location': 'Худжанд',
                'salary': '',
                'description': 'Создание макетов',
            },
        )
        created = Vacancy.objects.get(title='Дизайнер')
        detail_url = reverse('vakansia:vacancy_detail', args=(created.pk,))
        edit_url = reverse('vakansia:vacancy_update', args=(created.pk,))
        delete_url = reverse('vakansia:vacancy_delete', args=(created.pk,))
        self.assertRedirects(
            create_response,
            detail_url,
        )
        self.assertContains(self.client.get(edit_url), f'href="{detail_url}"')
        self.assertContains(self.client.get(delete_url), f'href="{detail_url}"')

        update_response = self.client.post(
            edit_url,
            {
                'title': 'Старший дизайнер',
                'company': 'Студия',
                'category': self.category.pk,
                'location': 'Худжанд',
                'salary': '',
                'description': 'Создание макетов',
            },
        )
        created.refresh_from_db()
        self.assertEqual(created.title, 'Старший дизайнер')
        self.assertRedirects(
            update_response,
            detail_url,
        )

        delete_response = self.client.post(
            delete_url,
        )
        self.assertRedirects(delete_response, reverse('vakansia:vacancy_list'))
        self.assertFalse(Vacancy.objects.filter(pk=created.pk).exists())

    def test_applicant_can_apply_to_multiple_vacancies(self):
        second_vacancy = Vacancy.objects.create(
            category=self.category,
            title='Django-разработчик',
            company='Другой работодатель',
            description='Разработка',
        )

        first_response = self.client.post(
            reverse('vakansia:vacancy_detail', args=(self.vacancy.pk,)),
            {
                'name': 'Алина',
                'email': 'alina@example.com',
                'phone': '+992 900 000 000',
                'message': 'Есть опыт работы.',
            },
        )
        second_response = self.client.post(
            reverse('vakansia:vacancy_detail', args=(second_vacancy.pk,)),
            {
                'name': 'Алина',
                'email': 'alina@example.com',
                'phone': '+992 900 000 000',
                'message': 'Есть опыт работы.',
            },
        )

        self.assertRedirects(
            first_response,
            reverse('vakansia:vacancy_detail', args=(self.vacancy.pk,)),
        )
        self.assertRedirects(
            second_response,
            reverse('vakansia:vacancy_detail', args=(second_vacancy.pk,)),
        )
        application = Request.objects.get(email='alina@example.com')
        self.assertSetEqual(
            set(application.vacancies.all()),
            {self.vacancy, second_vacancy},
        )
        self.assertEqual(Request.objects.filter(email='alina@example.com').count(), 1)

    def test_category_cannot_be_deleted_while_vacancies_use_it(self):
        response = self.client.post(
            reverse('vakansia:category_delete', args=(self.category.pk,)),
        )

        self.assertRedirects(response, reverse('vakansia:category_list'))
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

    def test_vacancy_form_explains_and_recovers_from_empty_categories(self):
        self.vacancy.delete()
        self.category.delete()

        response = self.client.get(reverse('vakansia:vacancy_create'))

        self.assertContains(response, 'Сначала создайте категорию')
        self.assertContains(
            response,
            'href="/categories/add/?next=/vacancies/add/"',
        )
        self.assertContains(response, 'disabled')
        self.assertNotContains(response, 'name="category"')

        create_category_url = (
            f'{reverse("vakansia:category_create")}'
            f'?next={reverse("vakansia:vacancy_create")}'
        )
        response = self.client.post(
            create_category_url,
            {'name': 'IT'},
        )

        self.assertRedirects(response, reverse('vakansia:vacancy_create'))
        self.assertContains(
            self.client.get(reverse('vakansia:vacancy_create')),
            'Выберите категорию',
        )

    def test_category_create_rejects_external_next_redirect(self):
        response = self.client.post(
            f'{reverse("vakansia:category_create")}?next=https://example.com',
            {'name': 'Безопасность'},
        )

        self.assertRedirects(response, reverse('vakansia:category_list'))

    def test_category_crud_and_return_links(self):
        category_list_url = reverse('vakansia:category_list')
        create_url = reverse('vakansia:category_create')
        response = self.client.get(create_url)
        self.assertContains(response, f'href="{category_list_url}"')

        response = self.client.post(create_url, {'name': 'Дизайн'})
        category = Category.objects.get(name='Дизайн')
        self.assertRedirects(response, category_list_url)

        update_url = reverse('vakansia:category_update', args=(category.pk,))
        response = self.client.post(update_url, {'name': 'Графический дизайн'})
        category.refresh_from_db()
        self.assertEqual(category.name, 'Графический дизайн')
        self.assertRedirects(response, category_list_url)

        delete_url = reverse('vakansia:category_delete', args=(category.pk,))
        response = self.client.get(delete_url)
        self.assertContains(response, f'href="{category_list_url}"')
        response = self.client.post(delete_url)
        self.assertRedirects(response, category_list_url)
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())
