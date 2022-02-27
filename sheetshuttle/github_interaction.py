"""Read and process GitHub configs in the github_interactions directory."""
import json
import os
import pathlib
from typing import Dict, List

import yaml
from github import Github

from jsonschema import validate
from sheetshuttle import github_objects, util


CONFIG_LIST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["issue", "pull request", "file"],
            }
        },
        "required": ["type"],
    },
    "minItems": 1,
}


class MissingAuthenticationVariable(Exception):
    """Raised when a GitHub authentication variable is missing."""


class GithubManager:
    """Manage github authentication and posting functionalities."""

    def __init__(
        self, key_file=".env", sources_dir="config/github_interactions"
    ) -> None:
        """
        Create a GithubManager object that stores the configuration and authenticate api.

        Args:
            key_file (str, optional): path to Google Sheets API user keys and
            tokens. Defaults to ".env".

            sources_dir (str, optional): path to where the configuration
            is stored. Defaults to "config/github_interactions"
        """
        self.key_file: str = key_file
        self.api = GithubManager.authenticate_api(self.key_file)
        self.config_dir = pathlib.Path(sources_dir)
        self.config_data: Dict[str, Dict] = {}
        self.issue_entries: List[github_objects.IssueEntry] = []
        self.pull_request_entries: List[github_objects.PullRequestEntry] = []
        self.file_entries: List[github_objects.FileEntry] = []

    def collect_config(self):
        """Update config_data with the contents of file in the config directory."""
        # get a list of all yaml and yml path objects in the config_dir
        config_files: List[pathlib.Path] = util.get_yaml_files(self.config_dir)
        for yaml_file in config_files:
            # Open yaml file as read
            with open(yaml_file, "r", encoding="utf-8") as config_file:
                loaded_list = yaml.safe_load(config_file)
                self.parse_config_list(loaded_list)
                self.config_data[yaml_file.stem] = loaded_list

    def parse_config_list(self, config_list: list):
        """Create and append github object entries to respective instance variables.

        Args:
            config_list (list): list of dictionaries for every github entry
        """
        # validate the config list against the json schema
        validate(instance=config_list, schema=CONFIG_LIST_SCHEMA)
        for config in config_list:
            # Initialize the correct github object for each config and add it to
            # its list
            if config["type"] == "issue":
                issue_entry = github_objects.IssueEntry(config)
                self.issue_entries.append(issue_entry)
            elif config["type"] == "pull request":
                pr_entry = github_objects.PullRequestEntry(config)
                self.pull_request_entries.append(pr_entry)
            elif config["type"] == "file":
                file_entry = github_objects.FileEntry(config)
                self.file_entries.append(file_entry)

    def post_issues(self):
        """Iterate and post all issues in the issue entries list."""
        for issue in self.issue_entries:
            issue.post(self.api)

    def post_pull_requests(self):
        """Iterate and post all pull requests in the pull requests entries list."""
        for pull_request in self.pull_request_entries:
            pull_request.post(self.api)

    def post_files(self):
        """Iterate and post all files in the pull files entries list."""
        for file in self.file_entries:
            file.post(self.api)

    def post_all(self):
        """Post all entries in issues, pull requests, and files."""
        self.post_issues()
        self.post_pull_requests()
        self.post_files()

    @staticmethod
    def authenticate_api(key_file):
        """Use credentials from key_file our environment authenticate access to a GitHub account.

        Args:
            key_file (str, optional): Path to file containing GitHub token.
            Can be either JSON or .env file
        """
        token = ""
        var_name = "GH_ACCESS_TOKEN"
        if key_file.endswith(".json"):
            with open(key_file, "r", encoding="utf-8") as input_file:
                try:
                    token = json.load(input_file)["gh_access_token"]
                except KeyError as exce:
                    print(f"ERROR: the key {var_name} does not exist in {key_file}.")
                    raise exce
        elif key_file.endswith(".env"):
            token = os.getenv(var_name)
            if not token:
                raise MissingAuthenticationVariable(
                    f"Variable {var_name} could not be found"
                )
        else:
            raise Exception(
                f"Unclear source of Sheets authentication keys {key_file}."
                + "Must be a .env or .json file"
            )

        return Github(token)
