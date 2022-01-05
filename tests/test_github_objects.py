"""Test functionalities in the github_objects module."""
import os
from datetime import datetime

import pytest
from github import Github
from jsonschema.exceptions import ValidationError
from gridgopher import github_objects, util

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
    # Check that GitHub token exists as environment variable
    token = os.getenv(ENV_VAR_NAME)
    util.gh_check_skip(token)
    api = Github(token)
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
    # Check that GitHub token exists as environment variable
    token = os.getenv(ENV_VAR_NAME)
    util.gh_check_skip(token)
    api = Github(token)
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
    token = os.getenv(ENV_VAR_NAME)
    util.gh_check_skip(token)
    api = Github(token)
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
    token = os.getenv(ENV_VAR_NAME)
    util.gh_check_skip(token)
    api = Github(token)
    repo = api.get_repo(TEST_REPO_NAME)
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
    assert (
        out
        == f'Warning: issue #{update_config["number"]} does not exist, update skipped\n'
    )


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
    token = os.getenv(ENV_VAR_NAME)
    util.gh_check_skip(token)
    api = Github(token)
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
    # Check that GitHub token exists as environment variable
    token = os.getenv(ENV_VAR_NAME)
    util.gh_check_skip(token)
    api = Github(token)
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
    token = os.getenv(ENV_VAR_NAME)
    util.gh_check_skip(token)
    api = Github(token)
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
    assert (
        out
        == f'Warning: PR #{update_config["number"]} does not exist, update skipped\n'
    )
