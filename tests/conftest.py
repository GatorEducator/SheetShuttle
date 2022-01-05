"""Implement fixtures and hooks for pytest session."""

import json
import pathlib
import pytest

from dotenv import load_dotenv

# pylint: disable=C0103,W0602
full_test_data = {}

# TODO: add guaranteed teardown for all issues/PRs/files, even if tests fail
# TODO: add dynamic way to check whether tests should be skipped based on
# environment variable


@pytest.hookimpl()
def pytest_sessionstart():
    """Read and collect test data as part of the global test data dictionary.

    Set environment variables if they exist in a .env file
    """
    load_dotenv(dotenv_path=".env")
    test_data_files = pathlib.Path("./tests/test_data").glob("*.json")
    for json_data_file in test_data_files:
        with open(json_data_file, "r", encoding="utf-8") as data_file:
            current_test_data = json.load(data_file)
            global full_test_data
            full_test_data[json_data_file.stem] = current_test_data


@pytest.fixture
def test_data():
    """Return full_test_data."""
    return full_test_data
