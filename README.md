Zolotariov Anastasia

# Самостоятельная: click + sqlite, вариант 6 — diary

Утилита-дневник: группа команд на click, заметки хранятся в sqlite через SQLAlchemy (файл `diary.db` создаётся при первом запуске).

## Установка

```
pip install -r requirements.txt
```

## Запуск

```
python diary.py add "Купить молоко"
python diary.py list
python diary.py delete 1
```

Пример:

```
$ python diary.py add "Купить молоко"
Заметка добавлена, id: 1
$ python diary.py list
1 | 17.10.2026 14:05 | Купить молоко
$ python diary.py delete 5
Error: заметки с id 5 нет
```

## Тесты

Тесты используют sqlite в памяти, файл на диске не создаётся.

```
pytest
```
