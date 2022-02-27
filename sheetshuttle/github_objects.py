"""Create the object oriented structure for issue trackers, pull requests, and files."""
from typing import Dict, List, Collection, Union

from github import Github
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.ContentFile import ContentFile
from github.GithubException import GithubException
from jsonschema import validate


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
        self.gh_object = None
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
            "body": {"type": "string", "minLength": 1},
        },
        "required": ["type", "action", "repo", "body"],
        "if": {"properties": {"action": {"const": "create"}}},
        "then": {
            "properties": {
                "title": {"type": "string", "minLength": 1},
                "labels": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "minItems": 1,
                },
            },
            "required": ["title"],
        },
        "else": {
            "properties": {
                "number": {"type": "integer"},
                "labels": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "minItems": 1,
                },
            },
            "required": ["number"],
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

        if self.action == "create":
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
        try:
            if self.action == "create":
                issue = IssueEntry.create_issue(
                    api_object, self.repo, self.title, self.body, self.labels
                )
            elif self.action == "update":
                issue = IssueEntry.update_issue(
                    api_object, self.repo, self.number, self.body, self.labels
                )
            else:
                raise Exception(f"Unknown action {self.action} in {self}")
            self.posted = True
            # Store the issue github object as instance variable
            self.gh_object = issue
        except GithubException:
            print(
                "Warning: a GitHub error occurred while posting an IssueEntry."
                f"Entry with the following configuration was NOT posted {self.config}."
            )

    @staticmethod
    def create_issue(
        api_object: Github,
        repo_name: str,
        title: str,
        body: str,
        labels: List[str] = None,
    ) -> Issue:
        """Post a new issue on GitHub and returns the created issue.

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
            new_issue = repo.create_issue(title=title, body=body, labels=labels)
        else:
            new_issue = repo.create_issue(title=title, body=body)

        return new_issue

    @staticmethod
    def update_issue(
        api_object: Github,
        repo_name: str,
        number: int,
        body: str,
        labels: List[str] = None,
    ) -> Union[Issue, None]:
        """Add a comment to an issue on GitHub and returns the issue.

        Args:
            api_object (Github): an authenticated GitHub object
            repo_name (str): name of the repo to post the issue to, structured as 'org/repo_name'
            number (int): number of the issue to comment on
            body (str): body contents of the comment
            labels (List[str], optional): List of labels to add to the issue tracker.
            Defaults to None.
        """
        repo = api_object.get_repo(repo_name)
        latest_issue_number = repo.get_issues(state="all")[0].number
        if number > latest_issue_number:
            print(
                f"Warning: issue #{number} in {repo_name} does not exist, update skipped"
            )
            return None
        issue = repo.get_issue(number=number)
        issue.create_comment(body)
        if labels:
            for label in labels:
                issue.add_to_labels(label)
        return issue


# pylint: disable=R0913
class FileEntry(Entry):
    """
    Implements file creation and push on GitHub.

    Inherits from Entry
    """

    SCHEMA = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "const": "file"},
            "action": {"type": "string", "enum": ["create", "update", "replace"]},
            "repo": {"type": "string", "pattern": r"^.+[^\s]\/[^\s].+$"},
            "path": {"type": "string", "minLength": 1},
            "content": {"type": "string", "minLength": 1},
            "branch": {"type": "string", "minLength": 1},
            "commit_message": {"type": "string", "minLength": 1},
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
        try:
            function_to_call = getattr(FileEntry, f"{self.action}_file")
            self.gh_object = function_to_call(
                api_object,
                self.repo,
                self.path,
                self.content,
                self.branch,
                self.commit_message,
            )
            self.posted = True
        except GithubException:
            print(
                "Warning: a GitHub error occurred while posting a FileEntry."
                f"Entry with the following configuration was NOT posted {self.config}."
            )

    @staticmethod
    def create_file(
        api_object: Github,
        repo_name: str,
        path: str,
        content: str,
        branch: str,
        commit_message="Add new file",
    ) -> Union[ContentFile, None]:
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
            print(
                f"Warning: file already exists, {path} was NOT created in {repo_name}:{branch}."
            )
            return None
        repo = api_object.get_repo(repo_name)
        response = repo.create_file(path, commit_message, content, branch)
        return response["content"]  # type: ignore[return-value]

    @staticmethod
    def update_file(
        api_object: Github,
        repo_name: str,
        path: str,
        added_content: str,
        branch: str,
        commit_message="Update file",
    ) -> Union[ContentFile, None]:
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
            print(
                f"Warning: file does not exist, {path} was NOT updated in {repo_name}:{branch}."
            )
            return None
        repo = api_object.get_repo(repo_name)
        contents = repo.get_contents(path)
        old_content = contents.decoded_content.decode("utf-8")  # type: ignore[union-attr]
        new_content = old_content + added_content
        response = repo.update_file(
            contents.path,  # type: ignore[union-attr]
            commit_message,
            new_content,
            contents.sha,  # type: ignore[union-attr]
            branch,
        )
        return response["content"]  # type: ignore[return-value]

    @staticmethod
    def replace_file(
        api_object: Github,
        repo_name: str,
        path: str,
        new_content: str,
        branch: str,
        commit_message="Replace file",
    ) -> Union[ContentFile, None]:
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
            print(
                f"Warning: file does not exist, {path} was NOT replaced in {repo_name}:{branch}."
            )
            return None
        repo = api_object.get_repo(repo_name)
        contents = repo.get_contents(path)
        response = repo.update_file(
            contents.path,  # type: ignore[union-attr]
            commit_message,
            new_content,
            contents.sha,  # type: ignore[union-attr]
            branch,
        )
        return response["content"]  # type: ignore[return-value]

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
            file_content = contents.pop(0)  # type: ignore[union-attr]
            if file_content.path == path:
                return True
            if file_content.type == "dir":
                contents.extend(  # type: ignore[union-attr]
                    repo.get_contents(
                        file_content.path, branch  # type: ignore[arg-type]
                    )
                )
        return False


class PullRequestEntry(Entry):
    """
    Implements pull request creation on GitHub.

    Inherits from Entry
    """

    SCHEMA = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "const": "pull request"},
            "action": {"type": "string", "enum": ["create", "update"]},
            "repo": {"type": "string", "pattern": r"^.+[^\s]\/[^\s].+$"},
            "body": {"type": "string", "minLength": 1},
        },
        "required": ["type", "action", "repo", "body"],
        "if": {"properties": {"action": {"const": "create"}}},
        "then": {
            "properties": {
                "title": {"type": "string", "minLength": 1},
                "base": {"type": "string", "minLength": 1},
                "head": {"type": "string", "minLength": 1},
            },
            "required": ["title", "base", "head"],
        },
        "else": {
            "properties": {
                "number": {"type": "integer"},
            },
            "required": ["number"],
        },
    }

    def parse_config(self):
        """Iterate through the entry configuration and assign instance variables."""
        self.type = "pull request"
        self.action = self.config["action"]
        self.repo = self.config["repo"]
        self.body = self.config["body"]
        if self.action == "create":
            self.title = self.config["title"]
            self.base = self.config["base"]
            self.head = self.config["head"]
            self.number = None
        else:
            self.number = self.config["number"]
            self.title = None
            self.base = None
            self.head = None

    def post(self, api_object):
        """Post the entry to GitHub.

        Args:
            api_object (Github): An authenticated Github object
        """
        try:
            if self.action == "create":
                pull_request = PullRequestEntry.create_pull_request(
                    api_object, self.repo, self.title, self.body, self.base, self.head
                )
            elif self.action == "update":
                pull_request = PullRequestEntry.update_pull_request(
                    api_object, self.repo, self.number, self.body
                )
            else:
                raise Exception(f"Unknown action {self.action} in {self}")
            self.posted = True
            self.gh_object = pull_request
        except GithubException:
            print(
                "Warning: a GitHub error occurred while posting a PullRequestEntry."
                f"Entry with the following configuration was NOT posted {self.config}."
            )

    @staticmethod
    def create_pull_request(
        api_object: Github, repo_name: str, title: str, body: str, base: str, head: str
    ) -> Union[PullRequest, None]:
        """Create a new pull request on GitHub.

        Args:
            api_object (Github): an authenticated GitHub object
            repo_name (str): name of the repo to post the issue to, structured as 'org/repo_name'
            title (str): title of the pull request
            body (str): description of the pull request
            base (str): the name of the branch to merge into
            head (str): the name of the branch to merge from
        """
        try:
            repo = api_object.get_repo(repo_name)
            pull_request = repo.create_pull(
                title=title, body=body, base=base, head=head
            )
        except GithubException:
            print(
                f"Warning: a GitHub error occurred while creating a pull request in {repo_name}."
                f"{title} was not created"
            )
            return None
        return pull_request

    @staticmethod
    def update_pull_request(
        api_object: Github,
        repo_name: str,
        number: int,
        body: str,
    ) -> Union[PullRequest, None]:
        """Add a comment to a pull request on GitHub.

        Args:
            api_object (Github): an authenticated GitHub object
            repo_name (str): name of the repo to post the issue to, structured as 'org/repo_name'
            number (int): number of the pull request to comment on
            body (str): body contents of the comment
            labels (List[str], optional): List of labels to add to the issue tracker.
            Defaults to None.
        """
        repo = api_object.get_repo(repo_name)
        latest_pr_number = repo.get_pulls(state="all")[0].number
        if number > latest_pr_number:
            print(
                f"Warning: PR #{number} in {repo_name} does not exist, update skipped"
            )
            return None
        pull_request = repo.get_pull(number=number)
        pull_request.create_issue_comment(body)
        return pull_request
