""" Создание функций, обрабатываемых в шаблонах. Не забыть прописать в settings"""
import datetime


""" Добавляет переменную с текущим годом. """
def year(request):
    year = datetime.datetime.today().year
    return {
        'year': year
    }