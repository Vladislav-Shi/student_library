from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from utils.exel_parse import get_raw_disciplines_plan
from .forms import SyllabusForm, BookFilterForm
from .models import Book, Syllabus, Discipline, UserFavorite, Author
from .tasks import get_books_for_program


# Create your views here.
class BookCreateView(View):
    """Вьюха создания книги"""
    template_name = 'add_book.html'

    def get(self, request):
        return render(self.request, self.template_name)


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class CreateSyllabusView(View):
    template_name = 'create_syllabus.html'

    def get(self, request):
        form = SyllabusForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SyllabusForm(request.POST, request.FILES)
        if form.is_valid():
            direction_of_study = form.cleaned_data['direction_of_study']
            university = form.cleaned_data['university']
            year = form.cleaned_data['year']

            syllabus = Syllabus.objects.create(
                direction_of_study=direction_of_study,
                university=university,
                year=year
            )
            excel_file = form.cleaned_data['excel_file']
            exel_list = get_raw_disciplines_plan(excel_file)
            disciplines = []
            for key in exel_list:
                disciplines.append(Discipline(title=key['Наименование'], syllabus=syllabus))
            Discipline.objects.bulk_create(disciplines)

            for discipline in disciplines:
                discipline.refresh_from_db()

            discipline_ids = [discipline.pk for discipline in disciplines]

            get_books_for_program.delay(discipline_ids)

            return render(request, 'index.html')
        else:
            for field, errors in form.errors.items():
                # field содержит имя поля, а errors список ошибок для этого поля
                print(f"Errors in {field}: {', '.join(errors)}")
        return render(request, self.template_name, {'form': form})


class BookList(LoginRequiredMixin, ListView):
    """Вьюха для поиска книг для направления"""
    template_name = 'book_list.html'
    model = Book
    context_object_name = 'books'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.GET.get('title')
        author = self.request.GET.get('author')
        par = self.request.GET.getlist('par')
        print('par', par)
        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(authors__name__icontains=author)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем форму фильтра в контекст
        context['form'] = BookFilterForm(self.request.GET)
        favs = Book.objects.filter(user_favorites__user=self.request.user,
                                   pk__in=[book.pk for book in context['books']])
        context['favs'] = [fav.google_id for fav in favs]
        context['home_path'] = self.request.build_absolute_uri(reverse('home'))
        return context


class BookListFavorite(LoginRequiredMixin, ListView):
    """Вьюха для вывода добавленных книг"""
    template_name = 'user_library.html'
    model = Book
    context_object_name = 'books'
    paginate_by = 20

    def get_queryset(self):
        queryset = UserFavorite.get_user_books(self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем форму фильтра в контекст
        context['form'] = BookFilterForm(self.request.GET)
        context['home_path'] = self.request.build_absolute_uri(reverse('home'))
        return context


class BaseCreateBook(View):
    def get(self, request):
        title = self.request.GET.get('title')
        authors = self.request.GET.getlist('author')
        pages = self.request.GET.getlist('pages')
        isbn = self.request.GET.getlist('isbn')

        if not title:
            return JsonResponse({'error': 'Нет названия'}, status=400)
        if not isbn:
            return JsonResponse({'error': 'Нет isbn'}, status=400)
        # authors_obj = Author.bulk_get_or_create(authors)
        # book_obj, _ = Book.objects.get_or_create(
        #     google_id=book["google_id"],
        #     defaults={
        #         'title': book['title'],
        #         'info_url': book['info_url'],
        #         'isbn': book['isbn'],
        #         'year': book['year'],
        #         'pages': book['pages'],
        #     }
        # )


@login_required
def add_to_favorites(request, book_id):
    """Сохраняет книгу в избранное"""
    book = Book.objects.get_or_none(google_id=book_id)
    if book is None:
        return JsonResponse({'error': 'Не найдена книга'}, status=404)
    if not UserFavorite.objects.filter(user=request.user, book=book).exists():
        # Если нет, создаем запись в UserFavorite
        UserFavorite.objects.create(user=request.user, book=book)
        return JsonResponse({'success': 'Книга добавлена в избранное'})
    return JsonResponse({'error': 'Книга уже добавлена в избранное'}, status=400)


@login_required
def delete_from_favorites(request, book_id):
    """Сохраняет книгу в избранное"""
    book = Book.objects.get_or_none(google_id=book_id)
    if book is None:
        return JsonResponse({'error': 'Не найдена книга'}, status=404)
    obj = UserFavorite.objects.filter(user=request.user, book=book)
    if obj.exists():
        obj.delete()
        return JsonResponse({'success': 'Книга убрана из избранное'})
    return JsonResponse({'error': 'Книга не добавлена'}, status=400)
