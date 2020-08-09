from __future__ import annotations

from collections import namedtuple
from datetime import timedelta
from typing import Union

from usc_lr_timer import google_sheets, talk_to_google

SubmitResult = namedtuple('SubmitResult', ('result', 'error'))


class Model(object):
    def __init__(self, journal: str, sheet_id: str, name: str):
        self._journal = journal
        self._sheet_id = sheet_id
        self._name = name
        self._duration = timedelta()
        self._manual_hours = 0
        self._manual_minutes = 0
        self._manual_seconds = 0
        self._semester_index = 0
        self._semesters = ['Fall', 'Spring']
        self._categories = []
        self._category_index = 0

    @property
    def duration(self) -> timedelta:
        return self._duration

    def increment_duration(self, seconds: int):
        self._duration = self._duration + timedelta(seconds=seconds)

    def reset_duration(self):
        self._duration = timedelta()

    @property
    def semesters(self) -> list[str]:
        return self._semesters[:]

    @property
    def categories(self) -> list[str]:
        return self._categories[:]

    @property
    def name(self) -> str:
        return self._name

    @property
    def journal(self) -> str:
        return self._journal

    @property
    def semester(self) -> str:
        return self._semesters[self._semester_index]

    @property
    def category(self) -> Union[None, str]:
        if self._category_index == 0:
            return None
        else:
            return self._categories[self._category_index]

    @property
    def manual_hours(self) -> int:
        return self._manual_hours

    @property
    def manual_minutes(self) -> int:
        return self._manual_minutes

    @property
    def manual_seconds(self) -> int:
        return self._manual_seconds

    @property
    def manual_duration(self) -> timedelta:
        return timedelta(
            hours=self.manual_hours,
            minutes=self.manual_minutes,
            seconds=self.manual_seconds,
        )

    def set_manual_hours(self, hours: int):
        self._manual_hours = hours

    def set_manual_minutes(self, minutes: int):
        self._manual_minutes = minutes

    def set_manual_seconds(self, seconds: int):
        self._manual_seconds = seconds

    def set_categories(self):
        status, result = talk_to_google.talk_to_google(
            google_sheets.get_categories, self._sheet_id,
        )
        if status == talk_to_google.Results.success:
            self._categories = [''] + result
        else:
            self._categories = []

    def set_semester_index(self, index: int):
        self._semester_index = index

    def set_category_index(self, index: int):
        self._category_index = index

    def submit(self, manual: bool) -> SubmitResult:
        if self.name is None:
            return SubmitResult(None, 'Name not chosen')
        if self.category is None:
            return SubmitResult(None, 'Category not chosen')
        if manual:
            if self.manual_minutes > 60:
                return SubmitResult(None, 'Minutes must be between 0 and 60')
            elif self.manual_seconds > 60:
                return SubmitResult(None, 'Seconds must be between 0 and 60')
            duration = self.manual_duration
        else:
            duration = self.duration

        seconds = duration.total_seconds()
        if seconds == 0:
            return SubmitResult(None, 'No time recorded')

        status, _ = talk_to_google.talk_to_google(
            google_sheets.add_time,
            spreadsheet_id=self._sheet_id,
            name=self.name,
            semester=self.semester,
            duration=duration,
            category=self.category,
        )
        return SubmitResult(status, None)
