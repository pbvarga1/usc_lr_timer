# coding=utf-8
"""Login feature tests."""
import json
from unittest.mock import Mock

from PySide2 import QtCore, QtWidgets
from py._path.local import LocalPath
import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from pytest_mock.plugin import MockFixture
from pytestqt.qtbot import QtBot

from usc_lr_timer.login import LoginDialog, Model


@pytest.fixture
def mock_journals(mocker: MockFixture, tmpdir: LocalPath):
    journals: LocalPath = tmpdir.join('journals.json')
    mocker.patch('usc_lr_timer.login.JOURNALS', str(journals))
    with journals.open('w') as stream:
        json.dump({'Law Review': 'abc123', 'RLSJ': 'xyz789'}, stream)


@pytest.fixture
def model(mocker: MockFixture, mock_journals) -> Model:
    model = Model()
    mock_set_names = mocker.patch.object(model, 'set_names')

    def set_names(*args, **kwargs):
        model._names = ['', 'Vincent']
        model._name_mapping = {'Vincent': '1234'}

    mock_set_names.side_effect = set_names
    return model


@pytest.fixture
def dialog(model: Model, qtbot: QtBot) -> LoginDialog:
    dialog = LoginDialog(model)
    return dialog


@pytest.fixture
def mock_critical(mocker: MockFixture):
    return mocker.patch('usc_lr_timer.login.QtWidgets.QMessageBox.critical')


scenarios('login.feature')


@given('the window')
def the_window(dialog: LoginDialog, qtbot: QtBot):
    """The window."""
    qtbot.add_widget(dialog)


@when('I select a journal')
def i_select_a_journal(dialog: LoginDialog):
    """I select a journal."""
    dialog.journals_cb.setCurrentIndex(1)


@when('select the name "Vincent"')
def select_the_name_vincent(dialog: LoginDialog):
    """select the name "Vincent"."""
    dialog.names_cb.setCurrentIndex(1)


@when(parsers.parse('type the pin "{pin}"'))
def type_the_pin(pin: str, dialog: LoginDialog, model: Model, qtbot: QtBot):
    """I type "pin"."""
    qtbot.keyClicks(dialog.pin_line, pin)


@when('click login')
def click_login(dialog: LoginDialog, qtbot: QtBot, mock_critical: Mock):
    """click login"""
    btn = dialog.button_box.button(QtWidgets.QDialogButtonBox.Ok)
    qtbot.mouseClick(btn, QtCore.Qt.LeftButton)


@then('an error is box is shown')
def an_error_is_box_is_shown(dialog: LoginDialog, mock_critical: Mock):
    """an error is box is shown."""
    mock_critical.assert_called_once_with(dialog, 'Failed', 'Incorrect Pin')


@then('the dialog is accepted')
def the_dialog_is_accepted(dialog: LoginDialog):
    """the dialog is accepted."""
    assert dialog.result() == dialog.Accepted


@then('there are names')
def there_are_names(dialog: LoginDialog):
    """there are names."""
    assert dialog.names_cb.count() > 0
