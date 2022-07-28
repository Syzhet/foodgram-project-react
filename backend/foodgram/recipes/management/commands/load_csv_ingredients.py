import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = ('Класс для автоматического заполненеия данных об ингредиентах,'
            'Из CSV файла расположенного в папке fodata на уровне проекта'
            )

    def handle(self, *args, **options):
        path_to = Path(settings.BASE_DIR, 'data', 'ingredients.csv')
        print(path_to)
        try:
            with open(path_to, 'r', encoding='UTF-8') as f:
                data = csv.DictReader(f, delimiter=',',
                                      skipinitialspace=True)
                has_rows = False
                for row in data:
                    has_rows = True
                    try:
                        row_list = list(row.values())
                        Ingredient.objects.get_or_create(
                            name=row_list[0],
                            measurement_unit=row_list[1]
                        )
                    except IntegrityError:
                        print(row)
                        return ('Ошибка в данных: '
                                f'строка №{data.line_num - 1}')
                if not has_rows:
                    return 'Файл пуст'
        except FileNotFoundError:
            raise CommandError('Файл отсутствует в директории data')
        return 'Данные обновлены'
