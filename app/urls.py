from django.urls import path

from .views import BookCreateView, IndexView, CreateSyllabusView, BookList, add_to_favorites, BookListFavorite, \
    delete_from_favorites

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('list/', BookList.as_view(),  name='book-list'),
    path('add/syll/', CreateSyllabusView.as_view(), name='syll-create'),
    path('add/book/', BookCreateView.as_view(), name='book-create'),
    path('favorite/', BookListFavorite.as_view(), name='favorite'),
    path('favorite/add/<str:book_id>/', add_to_favorites),
    path('favorite/delete/<str:book_id>/', delete_from_favorites),
]
