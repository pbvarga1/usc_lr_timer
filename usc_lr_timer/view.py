from __future__ import annotations

from PySide2.QtWidgets import QWidget

from usc_lr_timer.model import Model, SubmitResult


class View(object):
    def __init__(self, model: Model, widget: QWidget):
        self.model = model
        self.widget = widget

    def start_timer(self):
        self.widget.start_button.setEnabled(False)

    def pause_timer(self):
        self.widget.start_button.setEnabled(True)

    def set_categories(self):
        self.model.set_categories()
        self.widget.categories_cb.clear()
        self.widget.categories_cb.addItems(self.model.categories)

    def set_semester_index(self, index: int):
        self.model.set_semester_index(index)
        self.widget.semesters_cb.setCurrentIndex(index)

    def set_category_index(self, index: int):
        self.model.set_category_index(index)
        self.widget.categories_cb.setCurrentIndex(index)

    def set_manual_hours(self, hours: str):
        if hours == '':
            int_hours = 0
        else:
            int_hours = int(hours)
        self.model.set_manual_hours(int_hours)
        if hours == '':
            self.widget.hours_input.setText('')
        else:
            self.widget.hours_input.setText(f'{self.model.manual_hours:d}')

    def set_manual_minutes(self, minutes: str):
        if minutes == '':
            int_minutes = 0
        else:
            int_minutes = int(minutes)
        self.model.set_manual_minutes(int_minutes)
        if minutes == '':
            self.widget.minutes_input.setText('')
        else:
            self.widget.minutes_input.setText(f'{self.model.manual_minutes:d}')

    def set_manual_seconds(self, seconds: str):
        if seconds == '':
            int_seconds = 0
        else:
            int_seconds = int(seconds)
        self.model.set_manual_seconds(int_seconds)
        if seconds == '':
            self.widget.seconds_input.setText('')
        else:
            self.widget.seconds_input.setText(f'{self.model.manual_seconds:d}')

    def sync(self):
        self.set_categories()
        self.widget.semesters_cb.clear()
        self.widget.semesters_cb.addItems(self.model.semesters)
        self.set_manual_hours(self.model.manual_hours)
        self.set_manual_seconds(self.model.manual_seconds)
        self.set_manual_minutes(self.model.manual_minutes)
        self.set_duration_field()

    def increment_duration(self, seconds: int):
        self.model.increment_duration(seconds)
        self.set_duration_field()

    def set_duration_field(self):
        minutes, seconds = divmod(self.model.duration.total_seconds(), 60)
        hours, minutes = divmod(minutes, 60)
        self.widget.duration_field.setText(
            f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}'
        )

    def submit(self) -> SubmitResult:
        return self.model.submit(self.widget._tab_widget.currentIndex() == 1)

    def reset_timer(self):
        self.model.reset_duration()
        self.set_duration_field()
