from django.urls import path

from .views import BookCreateView, IndexView, CreateSyllabusView, BookList

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('list/', BookList.as_view(),  name='book-list'),
    path('add/syll/', CreateSyllabusView.as_view(), name='syll-create'),
    path('add/book/', BookCreateView.as_view(), name='book-create'),
]
