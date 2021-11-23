"""Read and process GitHub configs in the github_interactions directory."""
from github import Github

import pathlib
from typing import List, Dict
import json

import os
import yaml


class GithubManager:
    """Manage github authentication and posting functionalities."""

    def __init__(
        self, key_file=".env", sources_dir="config/github_interactions"
    ) -> None:
        """
        Create a GithubManager object that stores the configuration and
        authenticate api.

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

    def collect_config(self):
        """
        Update config_data with the contents of file in the config directory.
        """
        # get a list of all yaml and yml path objects in the config_dir
        full_data = {}
        config_files = []
        extensions = ["*.yaml", "*.yml"]
        for ext in extensions:
            config_files.extend(pathlib.Path(self.config_dir).glob(ext))
        for yaml_file in config_files:
            # Open yaml file as read
            with open(yaml_file, "r", encoding="utf-8") as config_file:
                config_data = yaml.safe_load(config_file)
                self.config_data[yaml_file.stem] = config_data

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
            with open(key_file, "r") as input_file:
                # FIXME: add try for key error
                token = json.load(input_file)["gh_access_token"]
        elif key_file.endswith(".env"):
            token = os.getenv(var_name)
            if not token:
                raise Exception(f"Variable {var_name} could not be found")
        else:
            raise Exception(
                f"Unclear source of Sheets authentication keys {key_file}."
                + "Must be a .env or .json file"
            )

        return Github(token)


class Entry:
    """Contain the information of a github post in the form of pull request,
    issue tracker, or file"""

    def __init__(self, config: Dict) -> None:
        """Initialize an Entry object using a configuration argument.add()

        Args:
            config (Dict): a dictionary with needed keys that follows the Entry schema.
        """


# repo = g.get_repo("AC-GopherBot/test-1")
# markdown_sample = """|    |   assignment1 |   assignment2 |   assignment3 |
# |---:|--------------:|--------------:|--------------:|
# |  0 |             4 |             6 |          1234 |
# |  1 |            87 |            45 |           357 |
# |  2 |           132 |          1234 |         43327 |
# """
# repo.create_issue(title="This is a very new issue", body=markdown_sample)
# issue = repo.get_issue(number=1)
# issue.create_comment("Hello from python\n" + markdown_sample)
