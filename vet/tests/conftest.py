import os
import shutil
import tempfile

import pytest

from vet.commands import Commands


@pytest.fixture(scope="function")
def dummy_repo():
    tempdir = tempfile.mkdtemp()
    try:
        # copy files from tests/resources/dummy_repo to tempdir
        dummy_repo_path = os.path.join(
            os.path.dirname(__file__),
            "resources",
            "dummy_repo",
        )
        os.system(f"rsync -a --include '.*' {dummy_repo_path}/ {tempdir}/")

        yield tempdir
    finally:
        shutil.rmtree(tempdir)


@pytest.fixture
def dummy_commands(dummy_repo):
    return Commands(root_dir=dummy_repo)


@pytest.fixture
def commands():
    return Commands()
