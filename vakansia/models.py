from django.db import models


class Category(models.Model):
    name = models.CharField('Название категории', max_length=100, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='vacancies',
        verbose_name='Категория',
    )
    title = models.CharField('Должность', max_length=150)
    company = models.CharField('Организация', max_length=150)
    location = models.CharField('Город', max_length=100, blank=True)
    salary = models.CharField('Зарплата', max_length=100, blank=True)
    description = models.TextField('Описание')
    created_at = models.DateTimeField('Опубликовано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'вакансия'
        verbose_name_plural = 'вакансии'

    def __str__(self):
        return f'{self.title} — {self.company}'


class Request(models.Model):
    name = models.CharField('Имя кандидата', max_length=120)
    email = models.EmailField('Электронная почта')
    phone = models.CharField('Телефон', max_length=30, blank=True)
    message = models.TextField('Сопроводительное письмо', blank=True)
    vacancies = models.ManyToManyField(
        Vacancy,
        related_name='requests',
        verbose_name='Вакансии',
    )
    created_at = models.DateTimeField('Дата отклика', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'отклик'
        verbose_name_plural = 'отклики'

    def __str__(self):
        return f'{self.name} — {self.email}'
