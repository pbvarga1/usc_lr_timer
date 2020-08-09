from codecs import encode
import os
import shutil
import sys
from glob import glob
from pathlib import Path

from invoke import task

SEARCH_PATH = Path('usc_lr_timer') / '**'
TEST_SEARCH_PATH = Path('tests') / '**'


def delete_pattern(pattern: str):
    paths = glob(str(pattern), recursive=True)
    for path in paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


@task
def clean_py(c):
    delete_pattern(SEARCH_PATH / '*.pyc')
    delete_pattern(SEARCH_PATH / '__pycache__')


@task
def clean_test(c):
    delete_pattern('.pytest_cache')
    delete_pattern('.coverage')


@task
def clean_build(c):
    delete_pattern('windows')


@task(clean_py, clean_test, clean_build)
def clean(c):
    pass


@task
def format(c):
    c.run('black usc_lr_timer')
    c.run('black tests')
    c.run('isort usc_lr_timer')
    c.run('isort tests')


@task
def lint(c):
    results = []
    results.append(c.run('black --check usc_lr_timer', warn=True))
    results.append(c.run('black --check tests', warn=True))
    results.append(c.run('isort --check usc_lr_timer', warn=True))
    results.append(c.run('isort --check tests', warn=True))
    results.append(c.run('flake8 usc_lr_timer', warn=True))
    results.append(c.run('flake8 tests', warn=True))
    return sys.exit(int(sum(res.exited for res in results) > 0))