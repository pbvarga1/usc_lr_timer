from unittest.mock import Mock

import pytest
from pytest_mock.plugin import MockFixture
from pytestqt.qtbot import QtBot

from usc_lr_timer.app import MainWindow
from usc_lr_timer.model import Model
from usc_lr_timer.talk_to_google import Results


@pytest.fixture
def model_mock_ttg(mocker: MockFixture):
    mock_ttg = mocker.patch('usc_lr_timer.model.talk_to_google.talk_to_google')
    mock_ttg.return_value = Results.success, ['testing']
    return mock_ttg


@pytest.fixture
def model(model_mock_ttg: Mock):
    model = Model('Law Review', 'abc123', 'Vincent')
    return model


@pytest.fixture
def window(model: Model, qtbot: QtBot):
    window = MainWindow(model)
    qtbot.add_widget(window)
    return window


@pytest.fixture
def view(window: MainWindow):
    return window.view
