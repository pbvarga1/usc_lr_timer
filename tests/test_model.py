from datetime import timedelta
from unittest.mock import Mock

from pytest_mock.plugin import MockFixture

from usc_lr_timer import google_sheets
from usc_lr_timer.model import Model, SubmitResult
from usc_lr_timer.talk_to_google import Results


def test_duration(model: Model):
    assert model.duration == timedelta()


def test_increment_duration(model: Model):
    model.increment_duration(1)
    assert model.duration == timedelta(seconds=1)
    model.increment_duration(2)
    assert model.duration == timedelta(seconds=3)


def test_reset_duration(model: Model):
    model._duration = timedelta(seconds=5)
    model.reset_duration()
    assert model.duration == timedelta()


def test_semesters(model: Model):
    assert model.semesters == ['Fall', 'Spring']
    assert model.semesters is not model._semesters
    assert model.semesters == model._semesters


def test_categories(model: Model):
    assert model.categories == []
    model._categories = ['a', 'b']
    assert model.categories == ['a', 'b']
    assert model.categories is not model._categories
    assert model.categories == model._categories


def test_name(model: Model):
    assert model.name == 'Vincent'


def test_journal(model: Model):
    assert model.journal == 'Law Review'


def test_semester(model: Model):
    assert model.semester == 'Fall'
    model._semester_index = 1
    assert model.semester == 'Spring'


def test_category(model: Model):
    assert model.category is None
    model._categories = ['', 'a']
    assert model.category is None
    model._category_index = 1
    assert model.category == 'a'


def test_manual_hours(model: Model):
    assert model.manual_hours == 0
    model._manual_hours = 1
    assert model.manual_hours == 1


def test_manual_minutes(model: Model):
    assert model.manual_minutes == 0
    model._manual_minutes = 1
    assert model.manual_minutes == 1


def test_manual_seconds(model: Model):
    assert model.manual_seconds == 0
    model._manual_seconds = 1
    assert model.manual_seconds == 1


def test_manual_duration(model: Model):
    assert model.manual_duration == timedelta()
    model._manual_hours = 1
    model._manual_minutes = 1
    model._manual_seconds = 1
    assert model.manual_duration == timedelta(hours=1, minutes=1, seconds=1)


def test_set_manual_hours(model: Model):
    assert model.manual_hours == 0
    model.set_manual_hours(1)
    assert model.manual_hours == 1


def test_set_manual_minutes(model: Model):
    assert model.manual_minutes == 0
    model.set_manual_minutes(1)
    assert model.manual_minutes == 1


def test_set_manual_seconds(model: Model):
    assert model.manual_seconds == 0
    model.set_manual_seconds(1)
    assert model.manual_seconds == 1


def test_set_categories(model: Model, model_mock_ttg: Mock):
    model.set_categories()
    #
    assert model.categories == ['', 'testing']
    model_mock_ttg.assert_called_once_with(
        google_sheets.get_categories, 'abc123',
    )
    model_mock_ttg.return_value = Results.error, None
    model.set_categories()
    assert model.categories == []


def test_set_semester_index(model: Model):
    assert model.semester == 'Fall'
    model.set_semester_index(1)
    assert model.semester == 'Spring'


def test_set_category_index(model: Model):
    model._categories = ['', 'a']
    assert model.category is None
    model.set_category_index(1)
    assert model.category == 'a'


def test_submit(model: Model, mocker: MockFixture):
    mock_ttg = mocker.patch('usc_lr_timer.model.talk_to_google.talk_to_google')
    mock_ttg.return_value = Results.success, None
    model._name = None
    assert model.submit(True) == SubmitResult(None, 'Name not chosen')
    model._name = 'Vincent'
    assert model.submit(True) == SubmitResult(None, 'Category not chosen')
    model._categories = ['', 'testing']
    model.set_category_index(1)
    model.set_manual_minutes(61)
    model.set_manual_seconds(61)
    result = SubmitResult(None, 'Minutes must be between 0 and 60')
    assert model.submit(True) == result
    model.set_manual_minutes(0)
    result = SubmitResult(None, 'Seconds must be between 0 and 60')
    assert model.submit(True) == result
    model.set_manual_seconds(0)
    assert model.submit(True) == SubmitResult(None, 'No time recorded')
    model.set_manual_seconds(42)
    assert model.submit(True) == SubmitResult(Results.success, None)
    mock_ttg.assert_called_with(
        google_sheets.add_time,
        spreadsheet_id='abc123',
        name='Vincent',
        semester='Fall',
        duration=timedelta(seconds=42),
        category='testing',
    )
    assert model.submit(False) == SubmitResult(None, 'No time recorded')
    model.increment_duration(24)
    assert model.submit(False) == SubmitResult(Results.success, None)
    mock_ttg.assert_called_with(
        google_sheets.add_time,
        spreadsheet_id='abc123',
        name='Vincent',
        semester='Fall',
        duration=timedelta(seconds=24),
        category='testing',
    )
