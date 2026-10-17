from datetime import datetime

import click
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


# функции работы с базой, сессию получают первым аргументом

def add_note(session, text):
    note = Note(text=text)
    session.add(note)
    session.commit()
    return note.id


def list_notes(session):
    return session.scalars(select(Note).order_by(Note.id)).all()


def delete_note(session, note_id):
    note = session.get(Note, note_id)
    if note is None:
        return False
    session.delete(note)
    session.commit()
    return True


def get_session():
    engine = create_engine("sqlite:///diary.db")
    Base.metadata.create_all(engine)  # при первом запуске создаст таблицу
    return Session(engine)


@click.group()
def cli():
    """Дневник с заметками"""


@cli.command()
@click.argument("text")
def add(text):
    """Добавить заметку"""
    if not text.strip():
        raise click.ClickException("текст заметки не может быть пустым")
    with get_session() as session:
        note_id = add_note(session, text)
    click.echo(f"Заметка добавлена, id: {note_id}")


@cli.command(name="list")
def show_notes():
    """Показать все заметки"""
    with get_session() as session:
        notes = list_notes(session)
        if not notes:
            click.echo("Заметок пока нет")
        for note in notes:
            date = note.created_at.strftime("%d.%m.%Y %H:%M")
            click.echo(f"{note.id} | {date} | {note.text}")


@cli.command()
@click.argument("note_id", type=int)
def delete(note_id):
    """Удалить заметку по id"""
    with get_session() as session:
        if not delete_note(session, note_id):
            raise click.ClickException(f"заметки с id {note_id} нет")
    click.echo(f"Заметка {note_id} удалена")


if __name__ == "__main__":
    cli()
