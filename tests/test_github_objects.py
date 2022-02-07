"""Test functionalities in the github_objects module."""
from datetime import datetime

import pytest
from jsonschema.exceptions import ValidationError
from mock_api import mock_gh_api
from sheetshuttle import github_objects, util

ENV_VAR_NAME = "GH_ACCESS_TOKEN"
TEST_REPO_NAME = "AC-GopherBot/test-1"
HEAD_BRANCH = "test_branch"
BASE_BRANCH = "main"


####################################
# ###### IssueEntry tests ##########
####################################


def test_issues_schema_no_error(test_data):
    """Check that Issues Entries are initialized correctly and schemas are validated."""
    data = test_data["issues_schema_test"]["passing"]
    for test_item in data:
        try:
            current_issue = github_objects.IssueEntry(test_item)
        except ValidationError as val_error:
            # Catch the error and fail the test
            assert False, f"Validating {test_item} caused an error. \n {val_error}"
        assert current_issue.config == test_item


def test_issues_schema_throws_error(test_data):
    """Check that Issues Entries are initialized correctly and schemas are validated."""
    data = test_data["issues_schema_test"]["failing"]
    for test_item in data:
        with pytest.raises(ValidationError):
            github_objects.IssueEntry(test_item)


def test_create_update_issue_with_lables():
    """Check that issues with labels can be created and updated on a sample repo."""
    api = mock_gh_api.MockGH()
    # Setup issue creation
    create_config = {
        "type": "issue",
        "action": "create",
        "repo": TEST_REPO_NAME,
        "title": "test create issue",
        "body": f"Test issue create on {datetime.now()}",
        "labels": ["automated testing"],
    }
    issue_entry = github_objects.IssueEntry(create_config)
    issue_entry.post(api)
    # Assert issue was posted with labels
    assert issue_entry.gh_object.title == create_config["title"]
    assert issue_entry.gh_object.body == create_config["body"]
    assert issue_entry.gh_object.labels[0].name == create_config["labels"][0]
    assert issue_entry.gh_object.state == "open"
    # setup issue update
    update_config = {
        "type": "issue",
        "action": "update",
        "repo": TEST_REPO_NAME,
        "number": issue_entry.gh_object.number,
        "body": f"Test issue updated on {datetime.now()}",
    }
    update_entry = github_objects.IssueEntry(update_config)
    update_entry.post(api)
    # Assert new results
    # check label wasn't changed
    assert update_entry.gh_object.labels[0].name == create_config["labels"][0]
    # Check the new comment body
    assert update_entry.gh_object.get_comments()[0].body == update_config["body"]
    # Teardown: close the issue
    issue_entry.gh_object.edit(state="closed")


def test_create_update_issue_no_lables():
    """Check that issues with no labels can be created and updated on a sample repo."""
    api = mock_gh_api.MockGH()
    # Setup issue creation
    create_config = {
        "type": "issue",
        "action": "create",
        "repo": TEST_REPO_NAME,
        "title": "test create issue",
        "body": f"Test issue create on {datetime.now()}",
    }
    issue_entry = github_objects.IssueEntry(create_config)
    issue_entry.post(api)
    # Assert issue was posted with labels
    assert issue_entry.gh_object.title == create_config["title"]
    assert issue_entry.gh_object.body == create_config["body"]
    assert len(issue_entry.gh_object.labels) == 0
    assert issue_entry.gh_object.state == "open"
    # setup issue update
    update_config = {
        "type": "issue",
        "action": "update",
        "repo": TEST_REPO_NAME,
        "number": issue_entry.gh_object.number,
        "body": f"Test issue updated on {datetime.now()}",
        "labels": ["automated testing"],
    }
    update_entry = github_objects.IssueEntry(update_config)
    update_entry.post(api)
    # Assert new results
    # Check the new comment body
    assert update_entry.gh_object.get_comments()[0].body == update_config["body"]

    # Teardown: close the issue
    issue_entry.gh_object.edit(state="closed")


def test_issue_post_unknown_action():
    """Check that post throws error for unknown action."""
    api = mock_gh_api.MockGH()
    # Setup issue creation
    create_config = {
        "type": "issue",
        "action": "create",
        "repo": TEST_REPO_NAME,
        "title": "test create issue",
        "body": f"Test issue create on {datetime.now()}",
        "labels": ["automated testing"],
    }
    issue_entry = github_objects.IssueEntry(create_config)
    # purposefully change action to provoke exception
    issue_entry.action = "nothing"
    with pytest.raises(Exception):
        issue_entry.post(api)


def test_update_nonexistent_issue(capfd):
    """Check that a warning is shown when trying to update a nonexistent issue."""
    api = mock_gh_api.MockGH()
    repo = api.get_repo(TEST_REPO_NAME)
    # !Note: this test can fail if the repo under test has no issues to start
    # !with. Mock API currently handles that
    latest_issue_number = repo.get_issues(state="all")[0].number
    # Setup issue creation
    update_config = {
        "type": "issue",
        "action": "update",
        "repo": TEST_REPO_NAME,
        "number": latest_issue_number + 1,
        "body": f"Test issue create on {datetime.now()}",
    }
    issue_entry = github_objects.IssueEntry(update_config)
    issue_entry.post(api)
    out, _ = capfd.readouterr()
    expected_out = (
        f'Warning: issue #{update_config["number"]} in'
        f" {TEST_REPO_NAME} does not exist, update skipped\n"
    )
    assert out == expected_out


####################################
# ## PullRequestEntry tests ########
####################################


def test_pr_schema_no_error(test_data):
    """Check that pull request Entries are initialized correctly and schemas are validated."""
    data = test_data["pr_schema_test"]["passing"]
    for test_item in data:
        try:
            current_issue = github_objects.PullRequestEntry(test_item)
        except ValidationError as val_error:
            # Catch the error if exists and fail the test
            assert False, f"Validating {test_item} caused an error. \n {val_error}"
        assert current_issue.config == test_item


def test_pr_schema_throws_error(test_data):
    """Check that pull request Entries are initialized correctly and schemas are validated."""
    data = test_data["pr_schema_test"]["failing"]
    for test_item in data:
        with pytest.raises(ValidationError):
            github_objects.PullRequestEntry(test_item)


def test_pr_post_unknown_action():
    """Check that post throws error for unknown action."""
    api = mock_gh_api.MockGH()
    # Setup issue creation
    create_config = {
        "type": "pull request",
        "action": "create",
        "repo": TEST_REPO_NAME,
        "title": "test create pull request",
        "body": f"Test pull request create on {datetime.now()}",
        "base": BASE_BRANCH,
        "head": HEAD_BRANCH,
    }
    issue_entry = github_objects.PullRequestEntry(create_config)
    # purposefully change action to provoke exception
    issue_entry.action = "nothing"
    with pytest.raises(Exception):
        issue_entry.post(api)


def test_create_update_pull_request():
    """Check that a pull request can be created and updated on a sample repo."""
    api = mock_gh_api.MockGH()
    # Setup issue creation
    create_config = {
        "type": "pull request",
        "action": "create",
        "repo": TEST_REPO_NAME,
        "title": "test create pull request",
        "body": f"Test pull request create on {datetime.now()}",
        "base": BASE_BRANCH,
        "head": HEAD_BRANCH,
    }
    pr_entry = github_objects.PullRequestEntry(create_config)
    pr_entry.post(api)
    # Assert issue was posted with labels
    assert pr_entry.gh_object.title == create_config["title"]
    assert pr_entry.gh_object.body == create_config["body"]
    assert len(pr_entry.gh_object.labels) == 0
    assert pr_entry.gh_object.state == "open"
    # setup issue update
    update_config = {
        "type": "pull request",
        "action": "update",
        "repo": TEST_REPO_NAME,
        "number": pr_entry.gh_object.number,
        "body": f"Test pull request updated on {datetime.now()}",
    }
    update_entry = github_objects.PullRequestEntry(update_config)
    update_entry.post(api)
    # Assert new results
    # Check the new comment body
    assert update_entry.gh_object.get_issue_comments()[0].body == update_config["body"]

    # Teardown: close the issue
    pr_entry.gh_object.edit(state="closed")


def test_update_nonexistent_pull_request(capfd):
    """Check that a warning is shown when trying to update a nonexistent pull request."""
    api = mock_gh_api.MockGH()
    repo = api.get_repo(TEST_REPO_NAME)
    latest_pr_number = repo.get_pulls(state="all")[0].number
    # Setup issue creation
    update_config = {
        "type": "pull request",
        "action": "update",
        "repo": TEST_REPO_NAME,
        "number": latest_pr_number + 1,
        "body": f"Test pr update on {datetime.now()}",
    }
    issue_entry = github_objects.PullRequestEntry(update_config)
    issue_entry.post(api)
    out, _ = capfd.readouterr()
    expected_out = (
        f'Warning: PR #{update_config["number"]} in'
        f" {TEST_REPO_NAME} does not exist, update skipped\n"
    )
    assert out == expected_out


####################################
# ##### FileEntry tests ############
####################################


def test_file_schema_no_error(test_data):
    """Check that file Entries are initialized correctly and schemas are validated."""
    data = test_data["file_schema_test"]["passing"]
    for test_item in data:
        try:
            current_file = github_objects.FileEntry(test_item)
        except ValidationError as val_error:
            # Catch the error and fail the test
            assert False, f"Validating {test_item} caused an error. \n {val_error}"
        assert current_file.config == test_item


def test_file_schema_throws_error(test_data):
    """Check that file Entries are initialized correctly and schemas are validated."""
    data = test_data["file_schema_test"]["failing"]
    for test_item in data:
        with pytest.raises(ValidationError):
            github_objects.FileEntry(test_item)


def test_file_create_update():
    """Check that a file can be created and updated on a sample GitHub Repo"""
    api = mock_gh_api.MockGH()
    create_file_path = "test_folder/test_file.md"
    # Make sure that the file doesn't already exist
    assert not github_objects.FileEntry.exists(
        api, TEST_REPO_NAME, create_file_path, BASE_BRANCH
    )
    # Create the file entry config and object
    create_time = str(datetime.now())
    create_config = {
        "type": "file",
        "action": "create",
        "repo": TEST_REPO_NAME,
        "path": create_file_path,
        "content": f"# hello world! \n**file created: {create_time}**",
        "branch": BASE_BRANCH,
        "commit_message": "test create file",
    }
    create_file_entry = github_objects.FileEntry(create_config)
    # Commit the file
    create_file_entry.post(api)
    # Check that it exists
    assert github_objects.FileEntry.exists(
        api, TEST_REPO_NAME, create_file_path, BASE_BRANCH
    )
    # Update the file
    update_time = str(datetime.now())
    update_config = {
        "type": "file",
        "action": "update",
        "repo": TEST_REPO_NAME,
        "path": create_file_path,
        "content": f"\n**file updated: {update_time}**",
        "branch": BASE_BRANCH,
        "commit_message": "test update file",
    }
    update_file_entry = github_objects.FileEntry(update_config)
    update_file_entry.post(api)
    # Check the latest contents of the file
    assert (
        update_file_entry.gh_object.decoded_content.decode("utf-8")
        == f"# hello world! \n**file created: {create_time}**\n**file updated: {update_time}**"
    )
    # Teardown and app deletion
    repo = api.get_repo(TEST_REPO_NAME)
    repo.delete_file(
        create_file_path,
        f"teardown test file {datetime.now()}",
        update_file_entry.gh_object.sha,
        BASE_BRANCH,
    )


def test_file_create_replace():
    """Check that a file can be created and replaced on a sample GitHub Repo"""
    api = mock_gh_api.MockGH()
    create_file_path = "test_folder/test_file.md"
    # Make sure that the file doesn't already exist
    assert not github_objects.FileEntry.exists(
        api, TEST_REPO_NAME, create_file_path, BASE_BRANCH
    )
    # Create the file entry config and object
    create_time = str(datetime.now())
    create_config = {
        "type": "file",
        "action": "create",
        "repo": TEST_REPO_NAME,
        "path": create_file_path,
        "content": f"# hello world! \n**file created: {create_time}**",
        "branch": BASE_BRANCH,
        "commit_message": "test create file",
    }
    create_file_entry = github_objects.FileEntry(create_config)
    # Commit the file
    create_file_entry.post(api)
    # Check that it exists
    assert github_objects.FileEntry.exists(
        api, TEST_REPO_NAME, create_file_path, BASE_BRANCH
    )
    # Update the file
    update_time = str(datetime.now())
    update_config = {
        "type": "file",
        "action": "replace",
        "repo": TEST_REPO_NAME,
        "path": create_file_path,
        "content": f"# hello world! \n**file replaced: {update_time}**",
        "branch": BASE_BRANCH,
        "commit_message": "test replace file",
    }
    update_file_entry = github_objects.FileEntry(update_config)
    update_file_entry.post(api)
    # Check the latest contents of the file
    assert (
        update_file_entry.gh_object.decoded_content.decode("utf-8")
        == f"# hello world! \n**file replaced: {update_time}**"
    )
    # Teardown and app deletion
    repo = api.get_repo(TEST_REPO_NAME)
    repo.delete_file(
        create_file_path,
        f"teardown test file {datetime.now()}",
        update_file_entry.gh_object.sha,
        BASE_BRANCH,
    )


def test_file_create_already_exists(capfd):
    """Assert warning is thrown when trying to create a file that already exists."""
    api = mock_gh_api.MockGH()
    existing_file_path = "folder/file.txt"
    # Make sure that the file doesn't already exist
    assert not github_objects.FileEntry.exists(
        api, TEST_REPO_NAME, existing_file_path, BASE_BRANCH
    )
    # Create the file entry config and object
    create_time = str(datetime.now())
    create_config = {
        "type": "file",
        "action": "create",
        "repo": TEST_REPO_NAME,
        "path": existing_file_path,
        "content": f"# hello world! \n**file created: {create_time}**",
        "branch": BASE_BRANCH,
        "commit_message": "test create file",
    }
    create_file_entry = github_objects.FileEntry(create_config)
    # Commit the file
    create_file_entry.post(api)
    # Check that it exists
    assert github_objects.FileEntry.exists(
        api, TEST_REPO_NAME, existing_file_path, BASE_BRANCH
    )
    create_config = {
        "type": "file",
        "action": "create",
        "repo": TEST_REPO_NAME,
        "path": existing_file_path,
        "content": "**Something**",
        "branch": BASE_BRANCH,
        "commit_message": "test create existing file",
    }
    create_file_entry = github_objects.FileEntry(create_config)
    # Commit the file
    create_file_entry.post(api)
    out, _ = capfd.readouterr()
    assert (
        out == f"Warning: file already exists, {existing_file_path} was"
        f" NOT created in {TEST_REPO_NAME}:{BASE_BRANCH}.\n"
    )


def test_file_update_nonexistent(capfd):
    """Assert warning is thrown when trying to update a nonexistent file."""
    api = mock_gh_api.MockGH()
    nonexisting_file_path = "random_folder/file.txt"
    assert not github_objects.FileEntry.exists(
        api, TEST_REPO_NAME, nonexisting_file_path, BASE_BRANCH
    )
    update_config = {
        "type": "file",
        "action": "update",
        "repo": TEST_REPO_NAME,
        "path": nonexisting_file_path,
        "content": "**Something**",
        "branch": BASE_BRANCH,
        "commit_message": "test update existing file",
    }
    update_file_entry = github_objects.FileEntry(update_config)
    # Commit the file
    update_file_entry.post(api)
    out, _ = capfd.readouterr()
    assert (
        out == f"Warning: file does not exist, {nonexisting_file_path} was"
        f" NOT updated in {TEST_REPO_NAME}:{BASE_BRANCH}.\n"
    )


def test_file_replace_nonexistent(capfd):
    """Assert warning is thrown when trying to replace a nonexistent file."""
    api = mock_gh_api.MockGH()
    nonexisting_file_path = "random_folder/file.txt"
    assert not github_objects.FileEntry.exists(
        api, TEST_REPO_NAME, nonexisting_file_path, BASE_BRANCH
    )
    replace_config = {
        "type": "file",
        "action": "replace",
        "repo": TEST_REPO_NAME,
        "path": nonexisting_file_path,
        "content": "**Something**",
        "branch": BASE_BRANCH,
        "commit_message": "test replace existing file",
    }
    replace_file_entry = github_objects.FileEntry(replace_config)
    # Commit the file
    replace_file_entry.post(api)
    out, _ = capfd.readouterr()
    assert (
        out == f"Warning: file does not exist, {nonexisting_file_path} was"
        f" NOT replaced in {TEST_REPO_NAME}:{BASE_BRANCH}.\n"
    )
