from __future__ import annotations

import sys

from PySide2 import QtCore, QtGui, QtWidgets

from usc_lr_timer import talk_to_google
from usc_lr_timer.constants import RESOURCES
from usc_lr_timer.login import login
from usc_lr_timer.model import Model
from usc_lr_timer.view import View


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, model: Model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._central_widget = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout()
        self.init_ui()
        self.init_controller()
        self._central_widget.setLayout(self._layout)
        self.setCentralWidget(self._central_widget)
        self.init_view(model)

    def _create_time_input(self, top: int):
        validator = QtGui.QIntValidator()
        validator.setBottom(0)
        if top is not None:
            validator.setTop(top)
        time_input = QtWidgets.QLineEdit()
        time_input.setValidator(validator)
        return time_input

    def init_ui(self):
        self.setWindowIcon(QtGui.QIcon(str(RESOURCES / 'icon.ico')))
        self.setWindowTitle('Timer')
        self.setWhatsThis('Track time worked on your journal')
        self.categories_cb = QtWidgets.QComboBox()
        self._categories_label = QtWidgets.QLabel('Category: ')
        self._categories_label.setBuddy(self.categories_cb)
        self._categories_layout = QtWidgets.QHBoxLayout()
        self._categories_layout.addWidget(self._categories_label)
        self._categories_layout.addWidget(self.categories_cb)
        self._layout.addLayout(self._categories_layout)

        # Add semester dropdown
        self.semesters_cb = QtWidgets.QComboBox()
        self._semesters_label = QtWidgets.QLabel('Semester: ')
        self._semesters_label.setBuddy(self.semesters_cb)
        self._semesters_layout = QtWidgets.QHBoxLayout()
        self._semesters_layout.addWidget(self._semesters_label)
        self._semesters_layout.addWidget(self.semesters_cb)
        self._layout.addLayout(self._semesters_layout)
        # self.semesters_cb.addItems(self.model.semesters)

        # Add tabs for timer or manual input
        self._tab_widget = QtWidgets.QTabWidget()
        self._layout.addWidget(self._tab_widget)

        # Create timer tab
        self._timer_widget = QtWidgets.QWidget()
        self._timer_layout = QtWidgets.QVBoxLayout()
        self._timer_widget.setLayout(self._timer_layout)
        self.start_button = QtWidgets.QPushButton('Start')
        self.pause_button = QtWidgets.QPushButton('Pause')
        self.reset_button = QtWidgets.QPushButton('Reset')
        self._button_layout = QtWidgets.QHBoxLayout()
        self._button_layout.addWidget(self.start_button)
        self._button_layout.addWidget(self.pause_button)
        self._button_layout.addWidget(self.reset_button)
        self._timer_layout.addLayout(self._button_layout)
        self.duration_field = QtWidgets.QLineEdit()
        self.duration_field.setReadOnly(True)
        self._timer_layout.addWidget(self.duration_field)
        self._tab_widget.addTab(self._timer_widget, 'Timer')

        # Create Manual Input tab
        self._manual_widget = QtWidgets.QWidget()
        self._manual_layout = QtWidgets.QFormLayout()
        self._manual_widget.setLayout(self._manual_layout)
        self.hours_input = self._create_time_input(None)
        self.minutes_input = self._create_time_input(60)
        self.seconds_input = self._create_time_input(60)
        self._manual_layout.addRow('Hours', self.hours_input)
        self._manual_layout.addRow('Minutes', self.minutes_input)
        self._manual_layout.addRow('Seconds', self.seconds_input)
        self._tab_widget.addTab(self._manual_widget, 'Manual')

        # Create submit button
        self._submit_button = QtWidgets.QPushButton('Submit')
        self._layout.addWidget(
            self._submit_button, alignment=QtCore.Qt.AlignRight,
        )

        # Create 1 second timer
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.update_duration)

    def init_controller(self):
        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.pause_timer)
        self.reset_button.clicked.connect(self.reset_timer)
        self._submit_button.clicked.connect(self.submit)
        self.semesters_cb.currentIndexChanged[int].connect(self.set_semester)
        self.categories_cb.currentIndexChanged[int].connect(self.set_category)
        self.hours_input.textEdited.connect(self.set_manual_hours)
        self.minutes_input.textEdited.connect(self.set_manual_minutes)
        self.seconds_input.textEdited.connect(self.set_manual_seconds)

    def init_view(self, model: Model):
        self.view = View(model, self)
        self.view.sync()

    def start_timer(self):
        self.view.start_timer()
        self._timer.start(1000)

    def pause_timer(self):
        self.view.pause_timer()
        self._timer.stop()

    def submit(self):
        if self._timer.isActive():
            was_active = True
            self.pause_timer()
        else:
            was_active = False
        result = self.view.submit()
        if result.error is not None:
            QtWidgets.QMessageBox.critical(self, 'Error', result)
            if was_active:
                self.start_timer()
        elif result.result == talk_to_google.Results.success:
            QtWidgets.QMessageBox.information(None, 'Success', 'Updated!')
            self.view.reset_timer()
            self.view.set_manual_hours(0)
            self.view.set_manual_minutes(0)
            self.view.set_manual_seconds(0)

    def reset_timer(self):
        res = QtWidgets.QMessageBox.question(
            self, 'Confirm Reset', 'Are you sure you want to reset your time?',
        )
        if res == QtWidgets.QMessageBox.Yes:
            self.pause_timer()
            self.view.reset_timer()

    def set_semester(self, index: int):
        self.view.set_semester_index(index)

    def set_category(self, index: int):
        self.view.set_category_index(index)

    def set_manual_hours(self, hours: str):
        self.view.set_manual_hours(hours)

    def set_manual_minutes(self, minutes: str):
        self.view.set_manual_minutes(minutes)

    def set_manual_seconds(self, seconds: str):
        self.view.set_manual_seconds(seconds)

    def update_duration(self):
        self.view.increment_duration(1)


def main():
    app = QtWidgets.QApplication([])

    success, journal, spreadsheet_id, name = login()

    if success:

        model = Model(journal, spreadsheet_id, name)

        window = MainWindow(model)
        window.show()

        sys.exit(app.exec_())
