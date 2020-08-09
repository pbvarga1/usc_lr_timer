from datetime import timedelta
from unittest.mock import Mock

from freezegun import freeze_time
from google.oauth2.service_account import Credentials
import pytest
from pytest_mock.plugin import MockFixture

from usc_lr_timer import google_sheets

PATH = 'usc_lr_timer.google_sheets.{}'


@pytest.fixture
def mock_values(mocker: MockFixture):
    mock_values = mocker.NonCallableMock()
    mocker.patch(
        PATH.format('get_spreadsheets_values'), return_value=mock_values,
    )
    return mock_values


def test_get_credentials(mocker: MockFixture):
    mock_from_service_account_file = mocker.patch(
        PATH.format('service_account.Credentials.from_service_account_file')
    )
    google_sheets.get_credentials()
    mock_from_service_account_file.assert_called_once_with(
        str(google_sheets.SERVICE_ACCOUNT_FILE),
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
    )


def test_get_spreadsheets_values(mocker: MockFixture):
    mock_creds = mocker.create_autospec(Credentials, instance=True)
    mocker.patch(PATH.format('get_credentials'), return_value=mock_creds)
    mock_resource = mocker.NonCallableMock()
    mock_build = mocker.patch(PATH.format('build'), return_value=mock_resource)
    mock_values = mock_resource.spreadsheets().values()
    values = google_sheets.get_spreadsheets_values()
    assert values is mock_values
    mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)


def test_read_sheet(mocker: MockFixture, mock_values: Mock):
    mock_request = mocker.Mock()
    mock_values.get.return_value = mock_request
    mock_request.execute.return_value = {'values': [1, 2, 3]}
    assert google_sheets.read_sheet('abc123', 'A1:A3') == [1, 2, 3]
    mock_values.get.assert_called_with(
        spreadsheetId='abc123', range='A1:A3',
    )


def test_add_row(mocker: MockFixture, mock_values: Mock):
    mock_request = mocker.Mock()
    mock_values.append.return_value = mock_request
    mock_request.execute.return_value = {'values': [1, 2, 3]}
    result = google_sheets.add_row('abc123', 'A1:A3', [1, 2, 3])
    mock_values.append.assert_called_with(
        spreadsheetId='abc123',
        range='A1:A3',
        valueInputOption='RAW',
        body={'values': [[1, 2, 3]]},
    )
    assert result == {'values': [1, 2, 3]}


def test_get_names(mocker: MockFixture, mock_values: Mock):
    mock_request = mocker.Mock()
    mock_values.get.return_value = mock_request
    mock_request.execute.return_value = {
        'values': [['a', '1'], ['b', '2'], ['c', '3']]
    }
    assert google_sheets.get_names('abc123') == {'a': '1', 'b': '2', 'c': '3'}
    mock_values.get.assert_called_once_with(
        spreadsheetId='abc123', range='Names!A2:B',
    )


def test_get_categories(mocker: MockFixture, mock_values: Mock):
    mock_request = mocker.Mock()
    mock_values.get.return_value = mock_request
    mock_request.execute.return_value = {'values': [['a'], ['b'], ['c']]}
    assert google_sheets.get_categories('abc123') == ['a', 'b', 'c']
    mock_values.get.assert_called_once_with(
        spreadsheetId='abc123', range='Categories!A2:A',
    )


@freeze_time('2020-10-24 12:13:14')
def test_add_time(mocker: MockFixture, mock_values: Mock):
    mock_request = mocker.Mock()
    mock_values.append.return_value = mock_request
    mock_request.execute.return_value = {'values': [1, 2, 3]}
    result = google_sheets.add_time(
        'abc123', 'Vincent', 'Fall', timedelta(days=1), 'testing',
    )
    mock_values.append.assert_called_with(
        spreadsheetId='abc123',
        range='Submissions',
        valueInputOption='RAW',
        body={
            'values': [
                ['Vincent', 'Fall', 1.0, '10/24/2020 12:13:14', 'testing']
            ]
        },
    )
    assert result == {'values': [1, 2, 3]}
