"""Create the object oriented structure for issue trackers, pull requests, and files."""
from typing import Dict, List, Collection

from github import Github
from jsonschema import validate  # type: ignore[import]

# TODO: update schema docs


class Entry:
    """Contain the interface and basic functions for a GitHub entry."""

    SCHEMA: Dict[str, Collection[str]] = {}

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
            "action": {"type": "string", "enum": ["create", "update"]},
            "repo": {"type": "string", "pattern": r"^.+[^\s]\/[^\s].+$"},
        },
        "required": ["type", "action", "repo"],
        "if": {"properties": {"action": {"const": "create"}}},
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
        if self.action == "create":
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


# pylint: disable=R0913
class FileEntry(Entry):
    """
    Implements file creation and push on GitHub.

    Inherits from Entry
    """

    # TODO: add support for file deletion if needed
    SCHEMA = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "const": "file"},
            "action": {"type": "string", "enum": ["create", "update", "replace"]},
            "repo": {"type": "string", "pattern": r"^.+[^\s]\/[^\s].+$"},
            "path": {"type": "string"},
            "content": {"type": "string"},
            "branch": {"type": "string"},
            "commit_message": {"type": "string"},
        },
        "required": ["type", "action", "repo", "path", "content", "branch"],
    }

    def parse_config(self):
        """Iterate through the entry configuration and assign instance variables."""
        self.type = "file"
        self.action = self.config["action"]
        self.repo = self.config["repo"]
        self.path = self.config["path"]
        self.content = self.config["content"]
        self.branch = self.config["branch"]
        if "commit_message" in self.config:
            self.commit_message = self.config["commit_message"]
        else:
            self.commit_message = f"{self.action} file: {self.path}"

    def post(self, api_object):
        """Post the entry to GitHub.

        Args:
            api_object (Github): An authenticated Github object
        """
        function_to_call = getattr(FileEntry, f"{self.action}_file")
        function_to_call(
            api_object,
            self.repo,
            self.path,
            self.content,
            self.branch,
            self.commit_message,
        )
        self.posted = True

    @staticmethod
    def create_file(
        api_object: Github,
        repo_name: str,
        path: str,
        content: str,
        branch: str,
        commit_message="Add new file",
    ):
        """Create a new file in a GitHub repository.

        Args:
            api_object (Github): an authenticated GitHub object
            repo_name (str): name of the repo to post the issue to, structured as 'org/repo_name'
            path (str): path to the file from the root of the repository
            contents (str): contents of the new file
            branch (str): name of the branch to create the file in
            commit_message (str, optional): Defaults to "Add new file"
        """
        if FileEntry.exists(api_object, repo_name, path, branch):
            print("Warning: file already exists, creation skipped")
            print(f"\t{path} was NOT created in {repo_name}:{branch}.")
            return
        repo = api_object.get_repo(repo_name)
        repo.create_file(path, commit_message, content, branch)

    @staticmethod
    def update_file(
        api_object: Github,
        repo_name: str,
        path: str,
        added_content: str,
        branch: str,
        commit_message="Update file",
    ):
        """Update an existing file in a GitHub repository.

        Args:
            api_object (Github): an authenticated GitHub object
            repo_name (str): name of the repo to post the issue to, structured as 'org/repo_name'
            path (str): path to the file from the root of the repository
            added_content (str): content to append to the file
            branch (str): name of the branch to create the file in
            commit_message (str, optional): Defaults to "Add new file"
        """
        if not FileEntry.exists(api_object, repo_name, path, branch):
            print("Warning: file does not exist, update skipped")
            print(f"\t{path} was NOT updated in {repo_name}:{branch}.")
            return
        repo = api_object.get_repo(repo_name)
        contents = repo.get_contents(path)
        new_content = contents.decoded_content.decode("utf-8") + added_content
        repo.update_file(
            contents.path, commit_message, new_content, contents.sha, branch
        )

    @staticmethod
    def replace_file(
        api_object: Github,
        repo_name: str,
        path: str,
        new_content: str,
        branch: str,
        commit_message="Replace file",
    ):
        """Replace the contents of a file in a GitHub repository.

        Args:
            api_object (Github): an authenticated GitHub object
            repo_name (str): name of the repo to post the issue to, structured as 'org/repo_name'
            path (str): path to the file from the root of the repository
            new_content (str): new contents of the file
            branch (str): name of the branch to create the file in
            commit_message (str, optional): Defaults to "Add new file"
        """
        if not FileEntry.exists(api_object, repo_name, path, branch):
            print("Warning: file does not exist, replace skipped")
            print(f"\t{path} was NOT replaced in {repo_name}:{branch}.")
            return
        repo = api_object.get_repo(repo_name)
        contents = repo.get_contents(path)
        repo.update_file(
            contents.path, commit_message, new_content, contents.sha, branch
        )

    @staticmethod
    def exists(api_object: Github, repo_name: str, path: str, branch: str) -> bool:
        """Check if a file or directory exists in the repository.

        Args:
            api_object (Github): an authenticated GitHub object
            repo_name (str): name of the repo to post the issue to, structured as 'org/repo_name'
            path (str): path to the file or directory from the root of the repository
            branch (str): branch to search in

        Returns:
            bool
        """
        repo = api_object.get_repo(repo_name)
        contents = repo.get_contents("", branch)
        while contents:
            file_content = contents.pop(0)
            if file_content.path == path:
                return True
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path, branch))
        return False
