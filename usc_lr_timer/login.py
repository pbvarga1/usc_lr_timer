from __future__ import annotations

import json
from typing import Union

from PySide2 import QtGui, QtWidgets

from usc_lr_timer import google_sheets, talk_to_google
from usc_lr_timer.constants import RESOURCES

JOURNALS = RESOURCES / 'journal_mapping.json'


class Model(object):
    def __init__(self):
        self._names = []
        self._name_index = 0
        self._name_mapping = {}
        self._journals = []
        self._journal_index = 0
        self._journal_mapping = {}
        self._pin = ''

    @property
    def names(self) -> list[str]:
        return self._names[:]

    @property
    def journals(self) -> list[str]:
        return self._journals[:]

    @property
    def name(self) -> Union[str, None]:
        if self._name_index == 0:
            return None
        else:
            return self._names[self._name_index]

    @property
    def journal(self) -> Union[str, None]:
        if self._journal_index == 0:
            return None
        else:
            return self._journals[self._journal_index]

    @property
    def sheet_id(self) -> Union[str, None]:
        if self.journal is None:
            return None
        else:
            return self._journal_mapping[self.journal]

    @property
    def pin(self) -> str:
        return self._pin

    def set_names(self):
        if self.sheet_id is not None:
            status, result = talk_to_google.talk_to_google(
                google_sheets.get_names, self.sheet_id,
            )
            if status == talk_to_google.Results.success:
                self._name_mapping = dict(result)
                self._names = [''] + list(self._name_mapping.keys())
                return

        self._name_mapping = {}
        self._names = []

    def set_journals(self):
        with open(JOURNALS) as stream:
            self._journal_mapping = json.load(stream)
        self._journals = [''] + list(self._journal_mapping.keys())

    def set_name_index(self, index: int):
        self._name_index = index

    def set_journal_index(self, index: int):
        self._journal_index = index

    def set_pin(self, pin: str):
        self._pin = pin

    def login(self) -> bool:
        if self.name is None:
            return False
        return self.pin == self._name_mapping[self.name]


class View(object):
    def __init__(self, model: Model, widget: LoginDialog):
        self.model = model
        self.widget = widget

    def set_names(self):
        self.model.set_names()
        self.widget.names_cb.clear()
        if self.model.journal:
            self.widget.names_cb.addItems(self.model.names)

    def set_journals(self):
        self.model.set_journals()
        self.widget.journals_cb.addItems(self.model.journals)

    def set_name_index(self, index: int):
        self.model.set_name_index(index)
        self.widget.names_cb.setCurrentIndex(index)

    def set_journal_index(self, index: int):
        self.model.set_journal_index(index)
        self.widget.journals_cb.setCurrentIndex(index)
        self.set_names()

    def set_pin(self, pin: str):
        self.model.set_pin(pin)

    def login(self) -> bool:
        if self.model.login():
            return True
        else:
            self.model.set_pin('')
            self.widget.pin_line.setText(self.model.pin)
            return False


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, model: Model):
        super().__init__(None)
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self.view = View(model, self)
        self.init_ui()
        self.init_controller()
        self.view.set_journals()
        self.view.set_names()

    def init_ui(self):
        self.setWindowIcon(QtGui.QIcon(str(RESOURCES / 'icon.ico')))
        self.setWindowTitle('Login')
        self.setWhatsThis('Login to track your time')
        form_layout = QtWidgets.QFormLayout()
        self.journals_cb = QtWidgets.QComboBox()
        form_layout.addRow('Journal: ', self.journals_cb)

        # Add names dropdown
        self.names_cb = QtWidgets.QComboBox()
        form_layout.addRow('Name: ', self.names_cb)

        # Add pin
        self.pin_line = QtWidgets.QLineEdit()
        self.pin_line.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow('Pin: ', self.pin_line)

        self._layout.addLayout(form_layout)

        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok
        )
        ok_btn = self.button_box.button(QtWidgets.QDialogButtonBox.Ok)
        ok_btn.setText('Login')
        self._layout.addWidget(self.button_box)

    def init_controller(self):
        self.names_cb.currentIndexChanged[int].connect(self.view.set_name_index)
        self.journals_cb.currentIndexChanged[int].connect(
            self.set_journal_index
        )
        self.pin_line.textEdited.connect(self.view.set_pin)
        self.button_box.accepted.connect(self.login)

    def set_journal_index(self, index: int):
        self.view.set_journal_index(index)

    def login(self):
        if self.view.login():
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, 'Failed', 'Incorrect Pin')


def login() -> tuple(bool, str, str, str):
    model = Model()
    dialog = LoginDialog(model)
    dialog.exec_()
    success = dialog.result() == dialog.Accepted
    return success, model.journal, model.sheet_id, model.name
