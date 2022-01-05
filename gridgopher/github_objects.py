"""Create the object oriented structure for issue trackers, pull requests, and files."""
from typing import Dict, List, Collection

from github import Github
from jsonschema import validate  # type: ignore[import]

# TODO: update schema docs
# TODO: update post functions to handle None return form create/update
# TODO: make sure that gh_object is consistent everywhere


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

    @staticmethod
    def create_issue(
        api_object: Github,
        repo_name: str,
        title: str,
        body: str,
        labels: List[str] = None,
    ):
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

    # TODO: what is the best way handle if issue doesn't exist?
    # Call the API and catch an exception if an error is found then tell the
    # user
    # OR get a list of all open and closed issues and check if the searched
    # number is highest than the current highest?
    @staticmethod
    def update_issue(
        api_object: Github,
        repo_name: str,
        number: int,
        body: str,
        labels: List[str] = None,
    ):
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
            print(f"Warning: issue #{number} does not exist, update skipped")
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
        if self.action == "create":
            PullRequestEntry.create_pull_request(
                api_object, self.repo, self.title, self.body, self.base, self.head
            )
        elif self.action == "update":
            PullRequestEntry.update_pull_request(
                api_object, self.repo, self.number, self.body
            )
        else:
            raise Exception(f"Unknown action {self.action} in {self}")
        self.posted = True

    # TODO: handle if PR already exists
    @staticmethod
    def create_pull_request(
        api_object: Github, repo_name: str, title: str, body: str, base: str, head: str
    ):
        """Create a new pull request on GitHub.

        Args:
            api_object (Github): an authenticated GitHub object
            repo_name (str): name of the repo to post the issue to, structured as 'org/repo_name'
            title (str): title of the pull request
            body (str): description of the pull request
            base (str): the name of the branch to merge into
            head (str): the name of the branch to merge from
        """
        repo = api_object.get_repo(repo_name)
        repo.create_pull(title=title, body=body, base=base, head=head)

    # TODO: what is the best way handle if PR doesn't exist?
    # Call the API and catch an exception if an error is found then tell the
    # user
    # OR get a list of all open and closed PRs and check if the searched
    # number is highest than the current highest?
    @staticmethod
    def update_pull_request(
        api_object: Github,
        repo_name: str,
        number: int,
        body: str,
    ):
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
        latest_issue_number = repo.get_issues(state="all")[0].number
        if number > latest_issue_number:
            print(f"Warning: PR #{number} does not exist, update skipped")
            return
        issue = repo.get_issue(number=number)
        issue.create_comment(body)
