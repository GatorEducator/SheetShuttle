"""Create the object oriented structure for issue trackers, pull requests, and files."""
from typing import Dict, List

from github import Github
from jsonschema import validate  # type: ignore[import]


class Entry:
    """Contain the interface and basic functions for a GitHub entry."""

    SCHEMA = None

    def __init__(self, config: Dict) -> None:
        """Initialize an Entry object using a configuration argument.

        Args:
            config (Dict): a dictionary with needed keys that follows the Entry schema.
        """
        self.validate_schema(config, type(self).SCHEMA)
        self.config = config
        self.posted = False
        self.parse_config()

    def parse_config(self):
        """Iterate through configuration and create appropriate variables.

        This method is not implemented, it sets an interface for inheriting
        classes.
        """

    def post(self, api_object):
        """Excecute the API request to post the item to GitHub.

        This method is not implemented, it sets an interface for inheriting
        classes.
        """

    @staticmethod
    def validate_schema(config, schema):
        """Check that the configuration follows the schema using jsonschema library.

        Args:
            config (Dict): Configuration to validate
            schema (Dict): Schema used for validation
        """
        validate(instance=config, schema=schema)


# pylint: disable=R0902
class IssueEntry(Entry):
    """
    Implements handling GitHub issue tracker creation and other functions.

    Inherits from Entry
    """

    SCHEMA = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "const": "issue"},
            "action": {"type": "string", "enum": ["new", "update"]},
            # TODO: might need a regex for repo name format "org/repo"
            "repo": {"type": "string"},
        },
        "required": ["type", "action", "repo"],
        "if": {"properties": {"action": {"const": "new"}}},
        "then": {
            "properties": {
                "title": {"type": "string", "minLength": 1},
                "body": {"type": "string", "minLength": 1},
                "labels": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "minItems": 1,
                },
            },
            "required": ["title", "body"],
        },
        "else": {
            "properties": {
                "number": {"type": "number"},
                "body": {"type": "string", "minLength": 1},
                "labels": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "minItems": 1,
                },
            },
            "required": ["number", "body"],
        },
    }

    def parse_config(self):
        """Iterate through the entry configuration and assign instance variables."""
        self.type = "issue"
        self.action = self.config["action"]
        self.repo = self.config["repo"]
        self.body = self.config["body"]
        if "labels" in self.config:
            self.labels = self.config["labels"]
        else:
            self.labels = None

        if self.action == "new":
            self.title = self.config["title"]
            self.number = None
        else:
            self.number = self.config["number"]
            self.title = None

    def post(self, api_object):
        """Post the entry to GitHub.

        Args:
            api_object (Github): An authenticated Github object
        """
        if self.action == "new":
            IssueEntry.create_new_issue(
                api_object, self.repo, self.title, self.body, self.labels
            )
        elif self.action == "update":
            IssueEntry.add_issue_comment(
                api_object, self.repo, self.number, self.body, self.labels
            )
        else:
            raise Exception(f"Unknown action {self.action} in {self}")
        self.posted = True

    @staticmethod
    def create_new_issue(
        api_object: Github,
        repo_name: str,
        title: str,
        body: str,
        labels: List[str] = None,
    ):
        """Post a new issue on GitHub.

        Args:
            api_object (Github): an authenticated GitHub object
            repo_name (str): name of the repo to post the issue to, structured as 'org/repo_name'
            title (str): title of the issue tracker
            body (str): body contents of the issue tracker
            labels (List[str], optional): List of labels to add to the issue tracker.
            Defaults to None.
        """
        repo = api_object.get_repo(repo_name)
        if labels:
            repo.create_issue(title=title, body=body, labels=labels)
        else:
            repo.create_issue(title=title, body=body)

        # TODO: is it useful to return the issue object?

    @staticmethod
    def add_issue_comment(
        api_object: Github,
        repo_name: str,
        number: int,
        body: str,
        labels: List[str] = None,
    ):
        """Add a comment to an issue on GitHub.

        Args:
            api_object (Github): an authenticated GitHub object
            repo_name (str): name of the repo to post the issue to, structured as 'org/repo_name'
            number (int): number of the issue to comment on
            body (str): body contents of the comment
            labels (List[str], optional): List of labels to add to the issue tracker.
            Defaults to None.
        """
        repo = api_object.get_repo(repo_name)
        issue = repo.get_issue(number=number)
        issue.create_comment(body)
        if labels:
            for label in labels:
                issue.add_to_labels(label)
        # TODO: is it useful to return the issue or comment object?
