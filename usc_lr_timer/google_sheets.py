from __future__ import annotations

from datetime import datetime, timedelta
from functools import lru_cache, reduce

from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource

from usc_lr_timer.constants import RESOURCES

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = RESOURCES / 'svc.json'
DATE_FMT = '%m/%d/%Y %H:%M:%S'


@lru_cache(1)
def get_credentials() -> service_account.Credentials:
    return service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE), scopes=SCOPES,
    )


def get_spreadsheets_values() -> Resource:
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    values = sheet.values()
    return values


def read_sheet(spreadsheet_id: str, sheet_range: str) -> list[list]:
    values = get_spreadsheets_values()
    result = values.get(
        spreadsheetId=spreadsheet_id, range=sheet_range,
    ).execute()
    return result['values']


def add_row(spreadsheet_id: str, name: str, values: list) -> dict:
    body = {'values': [values]}
    values = get_spreadsheets_values()
    result = values.append(
        spreadsheetId=spreadsheet_id,
        range=name,
        valueInputOption='RAW',
        body=body,
    ).execute()
    return result


def get_names(spreadsheet_id: str) -> dict[str, str]:
    return dict(read_sheet(spreadsheet_id, 'Names!A2:B'))


def get_categories(spreadsheet_id: str) -> list[str]:
    return reduce(
        lambda a, b: a + b, read_sheet(spreadsheet_id, 'Categories!A2:A')
    )


def add_time(
    spreadspreadsheet_id: str,
    name: str,
    semester: str,
    duration: timedelta,
    category: str,
) -> dict[str, str]:
    values = [
        name,
        semester,
        duration.total_seconds() / 60.0 / 60.0 / 24.0,
        datetime.now().strftime(DATE_FMT),
        category,
    ]
    return add_row(spreadspreadsheet_id, 'Submissions', values)
