import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from diary import Base, add_note, delete_note, list_notes


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_add_note_returns_id(session):
    note_id = add_note(session, "первая заметка")
    assert note_id == 1


def test_list_notes_empty(session):
    assert list_notes(session) == []


def test_list_notes_in_order(session):
    add_note(session, "раз")
    add_note(session, "два")
    add_note(session, "три")
    notes = list_notes(session)
    assert [note.text for note in notes] == ["раз", "два", "три"]


def test_note_has_created_at(session):
    add_note(session, "заметка с датой")
    note = list_notes(session)[0]
    assert note.created_at is not None


def test_delete_note_removes_existing_note(session):
    note_id = add_note(session, "удалить меня")
    assert delete_note(session, note_id) is True
    assert list_notes(session) == []


def test_delete_missing_note_returns_false(session):
    assert delete_note(session, 42) is False


def test_delete_only_one_note(session):
    first_id = add_note(session, "оставить")
    second_id = add_note(session, "удалить")
    delete_note(session, second_id)
    notes = list_notes(session)
    assert len(notes) == 1
    assert notes[0].id == first_id
