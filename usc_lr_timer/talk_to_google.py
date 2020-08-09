from __future__ import annotations

from collections.abc import Callable
from enum import IntEnum
from typing import Any

from PySide2 import QtCore, QtGui, QtWidgets

from usc_lr_timer.constants import RESOURCES
from usc_lr_timer.google_sheets import add_time, get_categories, get_names

ALLOWED_METHODS = [add_time, get_categories, get_names]


class Results(IntEnum):

    canceled = 1
    error = 2
    success = 3


class _Worker(QtCore.QRunnable):
    class Signals(QtCore.QObject):

        started = QtCore.Signal()
        finished = QtCore.Signal()

    def __init__(self, fn: Callable, *args, **kwargs):
        super().__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = self.Signals()
        self.result = None
        self.done = False
        self.exception = None

    @QtCore.Slot()
    def run(self):
        self.signals.started.emit()
        self.done = False
        self.result = None
        self.exception = None
        try:
            self.result = self.fn(*self.args, **self.kwargs)
        except Exception as exception:
            self.exception = exception
        finally:
            self.done = True
            self.signals.finished.emit()


def talk_to_google(fn: Callable, *args, **kwargs) -> tuple(Results, Any):
    if not callable(fn):
        raise TypeError(f'{fn} is not a callabe')
    if fn not in ALLOWED_METHODS:
        names = ", ".join([m.__name__ for m in ALLOWED_METHODS])
        raise ValueError(f'{fn.__name__} not in {names}')

    worker = _Worker(fn, *args, **kwargs)
    progress = QtWidgets.QProgressDialog('Talking to Google...', 'Stop', 0, 0)
    progress.setWindowIcon(QtGui.QIcon(str(RESOURCES / 'icon.ico')))
    worker.signals.finished.connect(progress.accept)
    threadpool = QtCore.QThreadPool()
    threadpool.start(worker)
    progress.exec_()
    if progress.wasCanceled():
        return Results.canceled, None
    elif worker.exception is not None:
        QtWidgets.QMessageBox.critical(None, 'Error', str(worker.exception))
        return Results.error, None
    else:
        return Results.success, worker.result
