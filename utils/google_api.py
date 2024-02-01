from typing import TypedDict, List, Optional

import requests


class BookModel(TypedDict):
    google_id: str
    title: str
    authors: List[str]
    photo_url: Optional[str]
    info_url: Optional[str]
    isbn: str
    pages: int
    year: int


def get_books_request(book_name: str, api_key: str) -> dict:
    """Запрашивает книги"""
    url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:{book_name}&key={api_key}'
    response = requests.get(url)
    if response.status_code == 400:
        raise ValueError('API ключ не подохдит!')
    return response.json()


def get_first_books_request(book_name: str, api_key: str, num_book: int = 10) -> list:
    """Возвращает первые n книг из запроса"""
    res = get_books_request(book_name, api_key)
    if 'items' not in res:
        raise ValueError('Пустой ответ')
    return res['items'][:num_book]


def parse_book(res: list) -> List[BookModel]:
    """Парсит книги"""
    books = []
    for item in res:
        authors = item['volumeInfo']['authors'] if 'authors' in item['volumeInfo'] else []
        pages = item['volumeInfo']['pageCount'] if 'pageCount' in item['volumeInfo'] else None
        year = item['volumeInfo']['publishedDate'] if 'publishedDate' in item['volumeInfo'] else None
        try:
            isbn = item['volumeInfo']['industryIdentifiers'][0]['identifier']
        except:
            isbn = None
        books.append({
            'google_id': item['id'],
            'title': item['volumeInfo']['title'],
            'authors': authors,
            'info_url': item['volumeInfo']['previewLink'],
            'isbn': isbn,
            'pages': pages,
            'year': year
        })
    return books


def get_book_for_id(book_id: str, api_key: str):
    """Получает информацию о книге по id"""
    pass
