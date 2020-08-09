"""Timer feature tests."""
from datetime import timedelta
from unittest.mock import Mock

from PySide2 import QtCore, QtWidgets
import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from pytest_mock.plugin import MockFixture
from pytestqt.qtbot import QtBot

from usc_lr_timer import google_sheets
from usc_lr_timer.app import MainWindow
from usc_lr_timer.model import Model
from usc_lr_timer.talk_to_google import Results

JOURNAL = 'Law Review'
SHEET_ID = 'abcdefg1234'
NAME = 'Vincent Vargas'


@pytest.fixture
def mock_progress(mocker: MockFixture, qtbot: QtBot):
    progress = QtWidgets.QProgressDialog('test', 'test', 0, 0)

    def exec_(*args, **kwargs):
        while progress.result() != progress.Accepted:
            qtbot.wait(200)

    mocker.patch.object(progress, 'exec_', side_effect=exec_)
    mock_Progress = mocker.patch(
        'usc_lr_timer.model.talk_to_google.QtWidgets.QProgressDialog',
        return_value=progress,
    )
    return mock_Progress


@pytest.fixture
def mock_talk_to_google(mocker: MockFixture, mock_progress: Mock):
    mock_talk_to_google = mocker.patch(
        'usc_lr_timer.model.talk_to_google.talk_to_google', autospec=True,
    )

    def talk_to_google(method, *args, **kwargs):
        if method is google_sheets.get_categories:
            return Results.success, ['testing', 'other']
        elif method is google_sheets.add_time:
            return Results.success, None
        else:
            raise NotImplementedError

    mock_talk_to_google.side_effect = talk_to_google
    return mock_talk_to_google


@pytest.fixture
def model(mock_talk_to_google: Mock):
    model = Model(JOURNAL, SHEET_ID, NAME)
    return model


scenarios('timer.feature')


@given('the window')
def window(model: Model, qtbot: QtBot, mocker: MockFixture):
    """the window."""
    message_box = 'usc_lr_timer.app.QtWidgets.QMessageBox.{}'
    mocker.patch(
        message_box.format('question'), return_value=QtWidgets.QMessageBox.Yes
    )
    mocker.patch(message_box.format('information'))
    window = MainWindow(model)
    qtbot.add_widget(window)
    return window


@given('the "Fall" semester')
def the_fall_semester(window: MainWindow):
    """the "Fall" semester."""
    window.semesters_cb.setCurrentIndex(0)


@given('the running timer')
def the_running_timer(window: MainWindow, qtbot: QtBot):
    """the running timer."""
    qtbot.mouseClick(window.start_button, QtCore.Qt.LeftButton)
    assert window._timer.isActive()
    qtbot.wait(1100)


@given('the user selects "testing" category')
def the_user_selects_testing_category(window: MainWindow):
    """the user selects "testing" category."""
    window.categories_cb.setCurrentIndex(1)


@given('the manual tab')
def the_manual_tab(window: MainWindow):
    window._tab_widget.setCurrentIndex(1)
    assert window._tab_widget.tabText(1) == 'Manual'


@given(
    parsers.parse(
        'the user enters'
        '\n"{hours}" for hours'
        '\n"{mins}" for minutes'
        '\n"{secs}" for seconds'
    )
)
def the_user_enters_time(
    hours: str, mins: str, secs: str, window: MainWindow, qtbot: QtBot
):
    qtbot.keyClicks(window.hours_input, hours)
    qtbot.keyClicks(window.minutes_input, mins)
    qtbot.keyClicks(window.seconds_input, secs)


@when('the user clicks pause')
def the_user_clicks_pause(window: MainWindow, qtbot: QtBot):
    """the user clicks pause."""
    qtbot.mouseClick(window.pause_button, QtCore.Qt.LeftButton)


@when('the user clicks reset')
def the_user_clicks_reset(window: MainWindow, qtbot: QtBot):
    """the user clicks reset."""
    qtbot.mouseClick(window.reset_button, QtCore.Qt.LeftButton)


@when('the user clicks submit')
def the_user_clicks_submit(window: MainWindow, qtbot: QtBot):
    """the user clicks submit."""
    qtbot.mouseClick(window._submit_button, QtCore.Qt.LeftButton)


@when('the user works')
def the_user_works(qtbot: QtBot):
    qtbot.wait(1100)


@then(parsers.parse('the duration is {value}'))
def the_duration_is(value: str, model: Model):
    """the duration"""
    seconds = model.duration.total_seconds()
    value = value.lower().strip()
    if value == '0':
        assert seconds == 0
    elif value == 'greater than 0':
        assert seconds > 0
    else:
        raise NotImplementedError('Can only check "0" or "greater than 0"')


@then(parsers.parse('the start button is {state}'))
def the_start_button_is(state: str, window: MainWindow):
    """the start button is disabled."""
    assert window.start_button.isEnabled() is (state.lower() == 'enabled')


@then(parsers.parse('the timer is {state}'))
def the_timer_is(state: str, window: MainWindow, model: Model):
    """the timer state"""
    state = state.lower().strip()
    assert window._timer.isActive() is (state == 'running')


@then(parsers.parse('the app submits the duration of {dur} seconds'))
def the_app_submits_the_duration(
    dur: str, mock_talk_to_google: Mock, mocker: MockFixture
):
    dur = dur.lower().strip()
    if dur == 'any':
        duration = mocker.ANY
    else:
        duration = timedelta(seconds=int(dur))
    mock_talk_to_google.assert_called_with(
        google_sheets.add_time,
        spreadsheet_id=SHEET_ID,
        name=NAME,
        semester='Fall',
        duration=duration,
        category='testing',
    )
    if dur == 'any':
        call = mock_talk_to_google.call_args_list[-1]
        assert call[1]['duration'].total_seconds() > 0


@then('the fields are reset')
def the_fields_are_reset(window: MainWindow):
    assert window.seconds_input.text() == '0'
    assert window.minutes_input.text() == '0'
    assert window.hours_input.text() == '0'
