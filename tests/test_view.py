from datetime import timedelta
from unittest.mock import Mock

from pytest_mock.plugin import MockFixture

from usc_lr_timer.app import MainWindow
from usc_lr_timer.model import Model
from usc_lr_timer.talk_to_google import Results
from usc_lr_timer.view import View


def test_start_timer(view: View, window: MainWindow):
    window.start_button.setEnabled(True)
    view.start_timer()
    assert not window.start_button.isEnabled()


def test_pause_timer(view: View, window: MainWindow):
    window.start_button.setEnabled(False)
    view.pause_timer()
    assert window.start_button.isEnabled()


def test_set_categories(
    view: View, window: MainWindow, model: Model, model_mock_ttg: Mock
):
    model_mock_ttg.return_value = Results.error, []
    view.set_categories()
    assert window.categories_cb.count() == 0
    assert model.categories == []
    model_mock_ttg.return_value = Results.success, ['a', 'b']
    view.set_categories()
    assert window.categories_cb.count() == 3
    assert model.categories == ['', 'a', 'b']


def test_semester_index(view: View, window: MainWindow, model: Model):
    view.set_semester_index(1)
    assert model.semester == 'Spring'
    assert window.semesters_cb.currentIndex() == 1
    view.set_semester_index(0)
    assert model.semester == 'Fall'
    assert window.semesters_cb.currentIndex() == 0


def test_set_category_index(view: View, window: MainWindow, model: Model):
    view.set_category_index(1)
    assert model.category == 'testing'
    assert window.categories_cb.currentIndex() == 1


def test_set_manual_hours(view: View, window: MainWindow, model: Model):
    view.set_manual_hours('1')
    assert model.manual_hours == 1
    assert window.hours_input.text() == '1'
    view.set_manual_hours('')
    assert model.manual_hours == 0
    assert window.hours_input.text() == ''


def test_set_manual_minutes(view: View, window: MainWindow, model: Model):
    view.set_manual_minutes('1')
    assert model.manual_minutes == 1
    assert window.minutes_input.text() == '1'
    view.set_manual_minutes('')
    assert model.manual_minutes == 0
    assert window.minutes_input.text() == ''


def test_set_manual_seconds(view: View, window: MainWindow, model: Model):
    view.set_manual_seconds('1')
    assert model.manual_seconds == 1
    assert window.seconds_input.text() == '1'
    view.set_manual_seconds('')
    assert model.manual_seconds == 0
    assert window.seconds_input.text() == ''


def test_sync(
    view: View, window: MainWindow, model: Model, model_mock_ttg: Mock
):
    model_mock_ttg.return_value = Results.success, ['a', 'b']
    model._semesters = ['Summer', 'Darkness']
    model.set_manual_hours(1)
    model.set_manual_minutes(2)
    model.set_manual_seconds(3)
    view.sync()
    sems = [
        window.semesters_cb.itemText(i)
        for i in range(window.semesters_cb.count())
    ]
    assert sems == ['Summer', 'Darkness']
    cats = [
        window.categories_cb.itemText(i)
        for i in range(window.categories_cb.count())
    ]
    assert cats == ['', 'a', 'b']
    assert window.hours_input.text() == '1'
    assert window.minutes_input.text() == '2'
    assert window.seconds_input.text() == '3'
    assert window.duration_field.text() == '00:00:00'


def test_increment_duration(view: View, window: MainWindow):
    view.increment_duration(1)
    assert window.duration_field.text() == '00:00:01'
    view.increment_duration(60)
    assert window.duration_field.text() == '00:01:01'


def test_set_duration_field(view: View, window: MainWindow, model: Model):
    model._duration = timedelta()
    view.set_duration_field()
    assert window.duration_field.text() == '00:00:00'
    model._duration = timedelta(hours=36, minutes=24, seconds=12)
    view.set_duration_field()
    assert window.duration_field.text() == '36:24:12'


def test_submit(
    view: View, model: Model, window: MainWindow, mocker: MockFixture
):
    mock_submit = mocker.patch.object(model, 'submit')
    view.submit()
    mock_submit.assert_called_once_with(False)
    window._tab_widget.setCurrentIndex(1)
    view.submit()
    mock_submit.assert_called_with(True)


def test_reset_timer(view: View, model: Model, window: MainWindow):
    model._duration = timedelta(hours=36, minutes=24, seconds=12)
    view.set_duration_field()
    assert window.duration_field.text() == '36:24:12'
    view.reset_timer()
    model.duration == timedelta()
    assert window.duration_field.text() == '00:00:00'
