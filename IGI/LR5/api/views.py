# api/views.py
from django.http import JsonResponse
from django.views import View
import requests
import logging

# Инициализация логгера для приложения api
logger = logging.getLogger(__name__)

class RandomUserAPIView(View):
    """
    Представление для получения данных о случайном фейковом пользователе
    с помощью RandomUser API.
    """
    def get(self, request, *args, **kwargs):
        try:
            response = requests.get('https://randomuser.me/api/')
            response.raise_for_status() # Вызывает исключение для ошибок HTTP (4xx или 5xx)
            data = response.json()
            logger.info("Успешно получены данные от RandomUser API.")
            return JsonResponse(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к RandomUser API: {e}")
            return JsonResponse({'error': 'Не удалось получить данные от RandomUser API'}, status=500)
        except ValueError as e:
            logger.error(f"Ошибка при парсинге JSON от RandomUser API: {e}")
            return JsonResponse({'error': 'Некорректный ответ от RandomUser API'}, status=500)

class OpenLibraryAPIView(View):
    """
    Представление для поиска книг с помощью Open Library API.
    Принимает параметр 'query' для поиска по названию.
    Пример: /api/search_books/?q=django
    """
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q', '')
        if not search_query:
            logger.warning("Запрос к Open Library API без параметра 'q'.")
            return JsonResponse({'error': 'Параметр "q" (запрос для поиска) обязателен.'}, status=400)

        api_url = f'http://openlibrary.org/search.json?title={search_query}'
        try:
            response = requests.get(api_url)
            response.raise_for_status() # Вызывает исключение для ошибок HTTP (4xx или 5xx)
            data = response.json()
            logger.info(f"Успешно получены данные от Open Library API для запроса: '{search_query}'.")
            return JsonResponse(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к Open Library API для '{search_query}': {e}")
            return JsonResponse({'error': 'Не удалось получить данные от Open Library API'}, status=500)
        except ValueError as e:
            logger.error(f"Ошибка при парсинге JSON от Open Library API для '{search_query}': {e}")
            return JsonResponse({'error': 'Некорректный ответ от Open Library API'}, status=500)
