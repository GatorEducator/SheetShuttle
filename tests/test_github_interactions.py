"""Test functionalities in the github_interaction module."""
import json
import os
import yaml

import pytest
from jsonschema.exceptions import ValidationError
from gridgopher import github_interaction, github_objects, util


ENV_VAR_NAME = "GH_ACCESS_TOKEN"


gh_skipable = pytest.mark.skipif(
    util.gh_token_exists(), reason="Github token not found"
)


@gh_skipable
def test_github_manager_init():
    """Check that a github manager object is initialized correctly."""
    my_manager = github_interaction.GithubManager()
    assert my_manager.key_file == ".env"
    assert my_manager.api
    assert not my_manager.config_data


@gh_skipable
def test_authenticate_api_no_error(tmp_path):
    """Check that a github object can be authenticated correctly."""
    # Check with .env argument
    assert github_interaction.GithubManager.authenticate_api(".env")
    # Check with temporary .json file
    temporary_directory = tmp_path / "keys_folder"
    temporary_directory.mkdir()
    temporary_json = temporary_directory / "github_key.json"
    gh_access_token = os.getenv("GH_ACCESS_TOKEN")
    creds_dict = {"gh_access_token": gh_access_token}
    with open(temporary_json, "w+", encoding="utf-8") as writefile:
        json.dump(creds_dict, writefile)
    assert github_interaction.GithubManager.authenticate_api(str(temporary_json))


def test_authenticate_api_throws_error():
    """Check that a github object authentication throws error."""
    with pytest.raises(Exception):
        github_interaction.GithubManager.authenticate_api(".yaml")


def test_authenticate_api_json_key_error(tmp_path):
    """Check that a key error is thrown when an invalid json is used to authenticate."""
    # Check with temporary .json file
    temporary_directory = tmp_path / "keys_folder"
    temporary_directory.mkdir()
    temporary_json = temporary_directory / "github_key.json"
    creds_dict = {"invalid_key": "something_invalid"}
    with open(temporary_json, "w+", encoding="utf-8") as writefile:
        json.dump(creds_dict, writefile)
    with pytest.raises(KeyError):
        github_interaction.GithubManager.authenticate_api(str(temporary_json))


@gh_skipable
def test_collect_config(tmp_path, test_data):
    """Check that yaml configuration is read correctly and github objects are initialized"""
    # Create a temporary config directory with two yaml files
    temp_config_directory = tmp_path / "github_configuration"
    temp_config_directory.mkdir()
    first_temp_yaml = temp_config_directory / "config1.yaml"
    second_temp_yaml = temp_config_directory / "config2.yaml"
    # write sample data to the config files
    first_config_data = test_data["collect_config_test"]["sample1"]
    second_config_data = test_data["collect_config_test"]["sample2"]
    with open(first_temp_yaml, "w+", encoding="utf-8") as writefile:
        yaml.dump(first_config_data, writefile)
    with open(second_temp_yaml, "w+", encoding="utf-8") as writefile:
        yaml.dump(second_config_data, writefile)
    # create github manager object with the directory as argument
    manager = github_interaction.GithubManager(sources_dir=str(temp_config_directory))
    assert (
        not manager.config_data
        and not manager.issue_entries
        and not manager.pull_request_entries
        and not manager.file_entries
    )
    manager.collect_config()
    assert len(manager.issue_entries) == 3 and isinstance(
        manager.issue_entries[0], github_objects.IssueEntry
    )
    assert len(manager.pull_request_entries) == 1 and isinstance(
        manager.pull_request_entries[0], github_objects.PullRequestEntry
    )
    assert len(manager.file_entries) == 1 and isinstance(
        manager.file_entries[0], github_objects.FileEntry
    )


@gh_skipable
def test_collect_config_schema_error(tmp_path, test_data):
    """Check that schema error is detecting when collecting yaml configuration"""
    # Create a temporary config directory with a yaml file
    temp_config_directory = tmp_path / "github_configuration"
    temp_config_directory.mkdir()
    temp_yaml = temp_config_directory / "config1.yaml"
    # write sample data to the config file
    config_data = test_data["collect_config_test"]["error_sample"]
    with open(temp_yaml, "w+", encoding="utf-8") as writefile:
        yaml.dump(config_data, writefile)
    # create github manager object with the directory as argument
    manager = github_interaction.GithubManager(sources_dir=str(temp_config_directory))
    assert (
        not manager.config_data
        and not manager.issue_entries
        and not manager.pull_request_entries
        and not manager.file_entries
    )
    with pytest.raises(ValidationError):
        manager.collect_config()


@gh_skipable
def test_post_all(test_data):
    """Check that all collected entries from config can be posted."""
    # create github manager object with the directory as argument
    manager = github_interaction.GithubManager()
    manager.parse_config_list(test_data["collect_config_test"]["postable_sample"])
    assert (
        len(manager.issue_entries) == 1
        and len(manager.pull_request_entries) == 1
        and len(manager.file_entries) == 1
    )
    # Post all available entries
    manager.post_all()
    # Check that a gh_object was created following a successful post
    assert (
        manager.issue_entries[0].gh_object
        and manager.pull_request_entries[0].gh_object
        and manager.file_entries[0].gh_object
    )
    # Teardown all created posts
    manager.issue_entries[0].gh_object.edit(state="closed")
    manager.pull_request_entries[0].gh_object.edit(state="closed")
    repo = manager.api.get_repo("AC-GopherBot/test-1")
    repo.delete_file(
        "folder1/file2.txt",
        "teardown test file",
        manager.file_entries[0].gh_object.sha,
        "main",
    )
