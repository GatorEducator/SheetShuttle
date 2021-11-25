"""Test functionalities in the github_interaction module."""
import json
import os

import pytest
from gridgopher import github_interaction


def test_github_manager_init():
    """Check that a github manager object is initialized correctly."""
    my_manager = github_interaction.GithubManager()
    assert my_manager.key_file == ".env"
    assert my_manager.api
    assert not my_manager.config_data


def test_authenticate_api_no_error(tmp_path):
    """Check that a github object can be authenticated correctly."""
    # Check with .env argument
    assert github_interaction.GithubManager.authenticate_api(".env")

    # Check with temporary .json file
    temporary_directory = tmp_path / "keys_folder"
    temporary_directory.mkdir()
    temporary_json = temporary_directory / "github_key.json"
    creds_dict = {"gh_access_token": os.getenv("GH_ACCESS_TOKEN")}
    with open(temporary_json, "w+", encoding="utf-8") as writefile:
        json.dump(creds_dict, writefile)
    assert github_interaction.GithubManager.authenticate_api(str(temporary_json))


def test_authenticate_api_throws_error():
    """Check that a github object authentication throws error."""
    with pytest.raises(Exception):
        github_interaction.GithubManager.authenticate_api(".yaml")
