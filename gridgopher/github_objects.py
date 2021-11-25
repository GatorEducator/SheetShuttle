"""Create the object oriented structure for issue trackers, pull requests, and files."""
from typing import Dict, List

from jsonschema import validate  # type: ignore[import]


class Entry:
    """Contain the interface and basic functions for a GitHub entry."""

    SCHEMA = None

    def __init__(self, config: Dict) -> None:
        """Initialize an Entry object using a configuration argument.add()

        Args:
            config (Dict): a dictionary with needed keys that follows the Entry schema.
        """
        self.validate_schema(config, type(self).SCHEMA)
        self.config = config
        self.parse_config()

    def parse_config(self):
        """Iterate through configuration and create appropriate variables.

        This method is not implemented, it sets an interface for inheriting
        classes."""
        pass

    def post(self):
        """Excecute the API request to post the item to GitHub.

        This method is not implemented, it sets an interface for inheriting
        classes."""
        pass

    @staticmethod
    def validate_schema(config, schema):
        validate(instance=config, schema=schema)


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
        self.type = "issue_tracker"
        # self.type = self.config["type"]
