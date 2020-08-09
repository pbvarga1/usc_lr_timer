from PySide2 import QtWidgets
import pytest
from pytest_mock.plugin import MockFixture
from pytestqt.qtbot import QtBot

from usc_lr_timer import talk_to_google

PATH = 'usc_lr_timer.talk_to_google.{}'


def test_worker(qtbot: QtBot):
    def fn(a, b):
        return {'foo': 'bar'}

    worker = talk_to_google._Worker(fn, 1, b=2)
    assert worker.args == (1,)
    assert worker.kwargs == {'b': 2}
    assert isinstance(worker.signals, talk_to_google._Worker.Signals)
    assert worker.result is None
    assert not worker.done
    assert worker.exception is None

    signals = [worker.signals.started, worker.signals.finished]
    with qtbot.wait_signals(signals, 2000):
        worker.run()

    assert worker.result == {'foo': 'bar'}
    assert worker.done
    assert worker.exception is None


def test_worker_exception(qtbot: QtBot):
    def fn():
        raise RuntimeError('Error')

    worker = talk_to_google._Worker(fn)
    assert worker.result is None
    assert not worker.done
    assert worker.exception is None

    signals = [worker.signals.started, worker.signals.finished]
    with qtbot.wait_signals(signals, 2000):
        worker.run()

    assert worker.result is None
    assert worker.done
    assert isinstance(worker.exception, RuntimeError)


def test_talk_to_google(qtbot: QtBot, mocker: MockFixture):
    def fn(a, b):
        return a + b

    mocker.patch(PATH.format('ALLOWED_METHODS'), [fn])
    progress = QtWidgets.QProgressDialog('test', 'test', 0, 0)

    def exec_(*args, **kwargs):
        while progress.result() != progress.Accepted:
            qtbot.wait(200)

    mock_exec = mocker.patch.object(progress, 'exec_', side_effect=exec_)
    mock_Progress = mocker.patch(
        PATH.format('QtWidgets.QProgressDialog'), return_value=progress
    )
    result, data = talk_to_google.talk_to_google(fn, 1, b=2)
    assert result == talk_to_google.Results.success
    assert data == 3
    mock_exec.assert_called_once_with()
    mock_Progress.assert_called_once_with('Talking to Google...', 'Stop', 0, 0)


def test_talk_to_google_error(qtbot: QtBot, mocker: MockFixture):
    def fn(a, b):
        raise RuntimeError('Test Exception')

    mocker.patch(PATH.format('ALLOWED_METHODS'), [fn])
    progress = QtWidgets.QProgressDialog('test', 'test', 0, 0)

    def exec_(*args, **kwargs):
        while progress.result() != progress.Accepted:
            qtbot.wait(200)

    mock_exec = mocker.patch.object(progress, 'exec_', side_effect=exec_)
    mock_Progress = mocker.patch(
        PATH.format('QtWidgets.QProgressDialog'), return_value=progress
    )
    mock_critical = mocker.patch(PATH.format('QtWidgets.QMessageBox.critical'))
    result, data = talk_to_google.talk_to_google(fn, 1, b=2)
    assert result == talk_to_google.Results.error
    assert data is None
    mock_exec.assert_called_once_with()
    mock_Progress.assert_called_once_with('Talking to Google...', 'Stop', 0, 0)
    mock_critical.assert_called_once_with(None, 'Error', 'Test Exception')


def test_talk_to_google_exception():
    with pytest.raises(TypeError):
        talk_to_google.talk_to_google(None)
    with pytest.raises(ValueError):
        talk_to_google.talk_to_google(lambda: None)


def test_talk_to_google_cancel(qtbot: QtBot, mocker: MockFixture):
    def fn(a, b):
        qtbot.wait(600)

    mocker.patch(PATH.format('ALLOWED_METHODS'), [fn])
    progress = QtWidgets.QProgressDialog('test', 'test', 0, 0)

    def exec_(*args, **kwargs):
        progress.cancel()

    mock_exec = mocker.patch.object(progress, 'exec_', side_effect=exec_)
    mock_Progress = mocker.patch(
        PATH.format('QtWidgets.QProgressDialog'), return_value=progress
    )
    result, data = talk_to_google.talk_to_google(fn, 1, b=2)
    assert result == talk_to_google.Results.canceled
    assert data is None
    mock_exec.assert_called_once_with()
    mock_Progress.assert_called_once_with('Talking to Google...', 'Stop', 0, 0)
