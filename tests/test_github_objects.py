import pytest
from gridgopher import github_objects
from jsonschema.exceptions import ValidationError


def test_issues_schema_no_error(test_data):
    """Check that Issues Entries are initialized correctly and schemas are validated."""
    data = test_data["issues_schema_test"]["passing"]
    for test_item in data:
        try:
            current_issue = github_objects.IssueEntry(test_item)
        except ValidationError as val_error:
            assert False, f"Validating {test_item} caused an error. \n {val_error}"
        assert current_issue.config == test_item


def test_issues_schema_no_error_throws_error(test_data):
    """Check that Issues Entries are initialized correctly and schemas are validated."""
    data = test_data["issues_schema_test"]["failing"]
    for test_item in data:
        with pytest.raises(ValidationError):
            github_objects.IssueEntry(test_item)
