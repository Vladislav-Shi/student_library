from datetime import datetime
from typing import List

from django.contrib.auth.models import User
from django.db import models


class YourModelManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


# Create your models here.
class Author(models.Model):
    """Модель автора книги"""
    name = models.CharField(verbose_name='имя автора', max_length=64, unique=True)
    description = models.TextField(verbose_name='информация об авторе', null=True, blank=True)

    objects = YourModelManager()

    @classmethod
    def bulk_get_or_create(cls, names_list: List[str]):
        authors_to_create = []
        # Сначала соберем авторов, которых нужно будет создать
        for name in names_list:
            author = cls(name=name)
            authors_to_create.append(author)
            # Получаем существующих авторов
        existing_authors = {author.name: author for author in
                            cls.objects.filter(name__in=[author.name for author in authors_to_create])}

        # Отфильтруем авторов, которые уже существуют
        authors_to_create = [author for author in authors_to_create if author.name not in existing_authors]

        # Создаем новых авторов
        cls.objects.bulk_create(authors_to_create)

        for author in authors_to_create:
            author.refresh_from_db()

        # Возвращаем всех авторов (существующих и только что созданных)
        return list(existing_authors.values()) + authors_to_create

    def __repr__(self) -> str:
        return f'{self.pk}:{self.name}'

    def __str__(self) -> str:
        return f'{self.pk}:{self.name}'

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'


class Book(models.Model):
    """Модель книги"""
    google_id = models.CharField(verbose_name='Google id', unique=True, max_length=64)
    title = models.CharField(verbose_name='Название книги', max_length=128)
    # т.к автор может быть и не указан и может быть больше одного
    authors = models.ManyToManyField(Author, verbose_name='список авторов')
    photo = models.ImageField(verbose_name='Обложка', null=True, blank=True)
    description = models.TextField(verbose_name='описание книги', null=True, blank=True)
    isbn = models.CharField(verbose_name='ISBN код', max_length=32, null=True, blank=True)
    info_url = models.URLField(verbose_name='Ссылка на книгу', null=True, blank=True)
    year = models.CharField(verbose_name='Год издания', max_length=16, null=True, blank=True)
    pages = models.IntegerField(verbose_name='Кол-во страниц', null=True, blank=True)

    objects = YourModelManager()

    def __repr__(self) -> str:
        return f'{self.pk}:{self.title}'

    def __str__(self) -> str:
        return f'{self.pk}:{self.title}'

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'


class Syllabus(models.Model):
    """Учебный план"""
    direction_of_study = models.CharField(verbose_name='направление обучения', max_length=128)
    university = models.CharField(verbose_name='университет', max_length=128)
    year = models.IntegerField(verbose_name='год принятия', default=datetime.now().year)

    def __repr__(self) -> str:
        return f'{self.pk}:{self.university} - {self.direction_of_study}. {self.year}'

    def __str__(self):
        return f'{self.pk}:{self.university} - {self.direction_of_study}. {self.year}'

    class Meta:
        verbose_name = 'Учебный план'
        verbose_name_plural = 'Учебные планы'


class Discipline(models.Model):
    title = models.CharField(verbose_name='название дисциплины', max_length=128)
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, verbose_name='учебный план')
    books = models.ManyToManyField(Book, verbose_name='список книг')

    def __repr__(self) -> str:
        return f'{self.pk}:{self.title}'

    def __str__(self) -> str:
        return f'{self.pk}:{self.title}:{self.syllabus.pk}'

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'


class UserFavorite(models.Model):
    """Добавленные книги"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Аккаунт', related_name='user_favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга', related_name='user_favorites')

    def __repr__(self) -> str:
        return f'{self.pk}:{self.user} - {self.book}'

    def __str__(self):
        return f'{self.pk}:{self.user} - {self.book}'

    @classmethod
    def get_user_books(cls, user) -> List[Book]:
        favs = cls.objects.filter(user=user)
        return [fav.book for fav in favs]
