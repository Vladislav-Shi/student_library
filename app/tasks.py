from typing import List

from celery.utils.log import get_task_logger
from django.conf import settings

from base.celery import app
from utils.google_api import get_first_books_request, parse_book
from .models import Discipline, Book, Author

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def get_books_for_program(discipline_ids: List[int]):
    disciplines = Discipline.objects.filter(id__in=discipline_ids)
    # for discipline in disciplines:
    for discipline in disciplines:
        try:
            json_res = get_first_books_request(discipline.title, settings.GOOGLE_API_KEY)
        except:
            continue
        json_res = parse_book(json_res)
        books = []
        for book in json_res:
            authors = Author.bulk_get_or_create(book['authors'])
            book_obj, _ = Book.objects.get_or_create(
                google_id=book["google_id"],
                defaults={
                    'title': book['title'],
                    'info_url': book['info_url'],
                    'isbn': book['isbn'],
                    'year': book['year'],
                    'pages': book['pages'],
                }
            )
            # book_obj.save()
            book_obj.authors.add(*authors)
            books.append(book_obj)
        discipline.books.add(*books)
