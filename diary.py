import logging
from contextlib import contextmanager
from datetime import datetime

import click
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

DB_URL = "sqlite:///diary.db"
LOG_FILE = "app.log"

logger = logging.getLogger("diary")


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


# бизнес-логика: функции получают сессию первым аргументом и ничего не знают про click


def add_note(session, text):
    text = text.strip()
    if not text:
        logger.warning("Попытка добавить пустую заметку")
        raise ValueError("текст заметки не может быть пустым")
    note = Note(text=text)
    session.add(note)
    session.commit()
    logger.info("Добавлена заметка id=%s", note.id)
    return note.id


def list_notes(session):
    notes = session.scalars(select(Note).order_by(Note.id)).all()
    logger.info("Запрошен список заметок, найдено: %s", len(notes))
    return notes


def delete_note(session, note_id):
    note = session.get(Note, note_id)
    if note is None:
        logger.warning("Заметка id=%s не найдена", note_id)
        return False
    session.delete(note)
    session.commit()
    logger.info("Удалена заметка id=%s", note_id)
    return True


def format_note(note):
    date = note.created_at.strftime("%d.%m.%Y %H:%M")
    return f"{note.id} | {date} | {note.text}"


# сессия для команд: при ошибке БД откатываем транзакцию, в конце всё закрываем


@contextmanager
def get_session():
    engine = create_engine(DB_URL)
    session = Session(engine)
    try:
        Base.metadata.create_all(engine)  # при первом запуске создаст таблицу
        yield session
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception("Ошибка базы данных")
        raise click.ClickException("ошибка базы данных, подробности в app.log") from e
    finally:
        session.close()
        engine.dispose()


@click.group()
def cli():
    """Дневник с заметками"""
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )


@cli.command()
@click.argument("text")
def add(text):
    """Добавить заметку"""
    try:
        with get_session() as session:
            note_id = add_note(session, text)
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    click.echo(f"Заметка добавлена, id: {note_id}")


@cli.command(name="list")
def show_notes():
    """Показать все заметки"""
    with get_session() as session:
        lines = [format_note(note) for note in list_notes(session)]
    if not lines:
        click.echo("Заметок пока нет")
    for line in lines:
        click.echo(line)


@cli.command()
@click.argument("note_id", type=click.IntRange(min=1))
def delete(note_id):
    """Удалить заметку по id"""
    with get_session() as session:
        deleted = delete_note(session, note_id)
    if not deleted:
        raise click.ClickException(f"заметки с id {note_id} нет")
    click.echo(f"Заметка {note_id} удалена")


if __name__ == "__main__":
    cli()
