Zolotariov Anastasia

# diary — CLI-дневник (вариант 6)

Утилита командной строки для ведения дневника: добавление, просмотр и удаление заметок. Написана на Click, заметки хранятся в SQLite через SQLAlchemy ORM. Файл базы `diary.db` и лог `app.log` создаются в папке, из которой запускается утилита.

## Установка

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

На Windows окружение активируется командой `.venv\Scripts\activate`.

## Использование

После `pip install -e .` доступна команда `diary`. Без установки можно запускать через `python diary.py`.

```
diary add "Купить молоко"
diary list
diary delete 1
diary --help
```

Пример работы:

```
$ diary add "Купить молоко"
Заметка добавлена, id: 1
$ diary list
1 | 22.10.2026 10:16 | Купить молоко
$ diary delete 5
Error: заметки с id 5 нет
$ echo $?
1
```

## Логи

Добавление, удаление и просмотр заметок, а также ошибки записываются в `app.log`.

## Тесты и проверка кода

```
pytest
ruff format --check .
ruff check .
```
