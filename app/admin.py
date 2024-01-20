from django.contrib import admin

from .models import Discipline, Author, Book, Syllabus

# Register your models here.

admin.site.register(Syllabus)
admin.site.register(Discipline)
admin.site.register(Book)
admin.site.register(Author)
