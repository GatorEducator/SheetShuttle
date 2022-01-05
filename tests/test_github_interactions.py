"""Test functionalities in the github_interaction module."""
import json
import os

import pytest
from gridgopher import github_interaction


def test_github_manager_init():
    """Check that a github manager object is initialized correctly."""
    try:
        my_manager = github_interaction.GithubManager()
    except github_interaction.MissingAuthenticationVariable:
        pytest.skip(
            "Authentication environment variable GH_ACCESS_TOKEN not found. Skipping test"
        )
    assert my_manager.key_file == ".env"
    assert my_manager.api
    assert not my_manager.config_data


def test_authenticate_api_no_error(tmp_path):
    """Check that a github object can be authenticated correctly."""
    # Check with .env argument
    try:
        assert github_interaction.GithubManager.authenticate_api(".env")
    except github_interaction.MissingAuthenticationVariable:
        pytest.skip(
            "Authentication environment variable GH_ACCESS_TOKEN not found. Skipping test"
        )
    # Check with temporary .json file
    temporary_directory = tmp_path / "keys_folder"
    temporary_directory.mkdir()
    temporary_json = temporary_directory / "github_key.json"
    gh_access_token = os.getenv("GH_ACCESS_TOKEN")
    if not gh_access_token:
        pytest.skip(
            "Authentication environment variable GH_ACCESS_TOKEN not found. Skipping test"
        )
    creds_dict = {"gh_access_token": gh_access_token}
    with open(temporary_json, "w+", encoding="utf-8") as writefile:
        json.dump(creds_dict, writefile)
    assert github_interaction.GithubManager.authenticate_api(str(temporary_json))


def test_authenticate_api_throws_error():
    """Check that a github object authentication throws error."""
    with pytest.raises(Exception):
        github_interaction.GithubManager.authenticate_api(".yaml")
