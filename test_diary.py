from datetime import datetime

import pytest
from click.testing import CliRunner
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import diary
from diary import Base, Note, add_note, cli, delete_note, format_note, list_notes


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


# бизнес-логика


def test_add_note_returns_id(session):
    assert add_note(session, "первая заметка") == 1


def test_add_note_strips_spaces(session):
    add_note(session, "  привет  ")
    assert list_notes(session)[0].text == "привет"


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_add_empty_note_raises_error(session, text):
    with pytest.raises(ValueError):
        add_note(session, text)
    assert list_notes(session) == []


def test_list_notes_empty(session):
    assert list_notes(session) == []


def test_list_notes_in_order(session):
    for text in ["раз", "два", "три"]:
        add_note(session, text)
    assert [note.text for note in list_notes(session)] == ["раз", "два", "три"]


def test_note_has_created_at(session):
    add_note(session, "заметка с датой")
    assert isinstance(list_notes(session)[0].created_at, datetime)


def test_delete_note_removes_existing_note(session):
    note_id = add_note(session, "удалить меня")
    assert delete_note(session, note_id) is True
    assert list_notes(session) == []


def test_delete_missing_note_returns_false(session):
    assert delete_note(session, 42) is False


def test_delete_note_twice(session):
    note_id = add_note(session, "заметка")
    assert delete_note(session, note_id) is True
    assert delete_note(session, note_id) is False


def test_delete_only_one_note(session):
    first_id = add_note(session, "оставить")
    second_id = add_note(session, "удалить")
    delete_note(session, second_id)
    notes = list_notes(session)
    assert len(notes) == 1
    assert notes[0].id == first_id


def test_format_note():
    note = Note(id=3, text="текст", created_at=datetime(2026, 10, 17, 9, 5))
    assert format_note(note) == "3 | 17.10.2026 09:05 | текст"


# команды CLI (во временной папке, чтобы не трогать настоящий diary.db)


def test_cli_add_and_list():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["add", "купить хлеб"])
        assert result.exit_code == 0
        result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "купить хлеб" in result.output


def test_cli_delete_missing_note_fails():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["delete", "5"])
    assert result.exit_code == 1
    assert "заметки с id 5 нет" in result.output


def test_cli_add_empty_text_fails():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["add", "   "])
    assert result.exit_code == 1
    assert "не может быть пустым" in result.output


def test_cli_delete_wrong_id_fails():
    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "0"])
    assert result.exit_code != 0


def test_cli_db_error_is_handled(monkeypatch):
    monkeypatch.setattr(diary, "DB_URL", "sqlite:///no_such_dir/diary.db")
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["list"])
    assert result.exit_code == 1
    assert "ошибка базы данных" in result.output
