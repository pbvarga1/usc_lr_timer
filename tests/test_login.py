import json
from unittest.mock import Mock

from py._path.local import LocalPath
import pytest
from pytest_mock.plugin import MockFixture

from usc_lr_timer.login import LoginDialog, Model
from usc_lr_timer.talk_to_google import Results

PATH = 'usc_lr_timer.login.{}'


@pytest.fixture
def mock_ttg(mocker: MockFixture):
    mock_ttg = mocker.patch(
        PATH.format('talk_to_google.talk_to_google'), autospec=True,
    )
    mock_ttg.return_value = Results.success, [['a', '1'], ['b', '2']]
    return mock_ttg


@pytest.fixture
def mock_journals(mocker: MockFixture, tmpdir: LocalPath):
    journals: LocalPath = tmpdir.join('journals.json')
    mocker.patch(PATH.format('JOURNALS'), str(journals))
    with journals.open('w') as stream:
        json.dump({'w': 'x', 'y': 'z'}, stream)


@pytest.fixture
def model():
    return Model()


@pytest.fixture
def dialog(model: Model, mock_journals: Mock, mock_ttg: Mock):
    return dialog


@pytest.fixture
def view(dialog: LoginDialog):
    return dialog.view


class TestModel(object):
    def test_names(self, model: Model):
        assert model.names == []
        model._names = ['', 'a', 'b']
        assert model.names == ['', 'a', 'b']

    def test_name(self, model: Model):
        assert model.name is None
        model._name_index = 1
        model._names = ['', 'a', 'b']
        assert model.name == 'a'

    def test_journals(self, model: Model):
        assert model.journals == []
        model._journals = ['', 'c', 'd']
        assert model.journals == ['', 'c', 'd']

    def test_journal(self, model: Model):
        model._journals = ['', 'c', 'd']
        assert model.journal is None
        model._journal_index = 1
        assert model.journal == 'c'

    def test_sheet_id(self, model: Model):
        model._journals = ['', 'c', 'd']
        model._journal_mapping = {'c': 'e', 'd': 'f'}
        assert model.sheet_id is None
        model._journal_index = 1
        assert model.sheet_id == 'e'

    def test_pin(self, model: Model):
        assert model.pin == ''
        model._pin = '1234'
        assert model.pin == '1234'

    def test_set_names(self, model: Model, mock_ttg: Mock):
        model._journals = ['', 'c', 'd']
        model._journal_mapping = {'c': 'e', 'd': 'f'}
        model._journal_index = 1
        model.set_names()
        assert model.names == ['', 'a', 'b']
        assert model._name_mapping == {'a': '1', 'b': '2'}

    def test_set_journals(self, model: Model, mock_journals: Mock):
        model.set_journals()
        assert model._journal_mapping == {'w': 'x', 'y': 'z'}
        assert model.journals == ['', 'w', 'y']

    def test_set_name_index(self, model: Model):
        model.set_name_index(1)
        assert model._name_index == 1

    def test_set_journal_index(self, model: Model):
        model.set_journal_index(1)
        assert model._journal_index == 1

    def test_set_pin(self, model: Model):
        model.set_pin('1234')
        assert model.pin == '1234'

    def test_login(self, model: Model):
        assert not model.login()
        model._names = ['', 'a']
        model._name_mapping = {'a': '1234'}
        model.set_name_index(1)
        model.set_pin('1234')
        assert model.login()
        model.set_pin('5678')
        assert not model.login()
