"""
Set up object oriented structure for Google Sheet data retrieval
"""

import json


class SheetsCollector:
    def __init__(self):
        self.config = {}

    # TODO: add other instance variables

    # TODO: fix the default path to be of object path type
    def read_config(self, config_file="config/sheets.json"):
        """
        Read config file and store contents in config instance variable

        Args:
            config_file: path to config file, defaults to the sheets.json
        """
        with open(config_file, "r") as f:
            self.config = json.load(f)
