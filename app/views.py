from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from utils.exel_parse import get_raw_disciplines
from .forms import SyllabusForm, BookFilterForm
from .models import Book, Syllabus, Discipline
from .tasks import get_books_for_program


# Create your views here.
class BookCreateView(CreateView):
    """Вьюха создания книги"""
    model = Book
    fields = ['title', 'author', 'description']


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
            exel_list = get_raw_disciplines(excel_file)
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


class BookList(ListView):
    """Вьюха для поиска книг для направления"""
    template_name = 'book_list.html'
    model = Book
    context_object_name = 'books'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.GET.get('title')
        authors = self.request.GET.getlist('authors')
        if title:
            queryset = queryset.filter(title__icontains=title)
        if authors:
            queryset = queryset.filter(authors__in=authors)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем форму фильтра в контекст
        context['form'] = BookFilterForm(self.request.GET)
        return context
