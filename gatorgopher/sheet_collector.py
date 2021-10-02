"""
Set up object oriented structure for Google Sheet data retrieval
"""

import json
import pandas
import pathlib
import yaml

from googleapiclient.discovery import build

# from google.oauth2.credentials import Credentials

from google.oauth2 import service_account


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SOURCES_DIR = "config/sheet_sources"


class SheetCollector:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.sheets = None
        self.config_dir = pathlib.Path(SOURCES_DIR)
        self.yaml_data = {}
        self.sheets_data = {}

    def authenticate(self, key_file="private/keys.json"):
        """Use credentials from key_file to authenticate access to a service account.

        Args:
            key_file (str, optional): Path to file containing API tokens.
                Defaults to "private/keys.json".
        """
        # TODO: add try statement for possible API errors
        self.credentials = service_account.Credentials.from_service_account_file(
            key_file, scopes=SCOPES
        )
        self.service = build("sheets", "v4", credentials=self.credentials)
        self.sheets = self.service.spreadsheets()

    def get_sheet(
        self, file_id: str, sheet_name: str, start_range: str, end_range: str
    ) -> pandas.DataFrame:
        """Get the specified range of a sheet as a pandas dataframe.

        Args:
            file_id (str): ID of the Google Sheet file
            sheet_name (str): Name of the sheet in the file
            start_range (str): Cell name to start from (eg. A4)
            end_range (str): Cell name to end at (eg. H5)

        Returns:
            pandas.DataFrame: Data found at the specified range
        """

        # TODO: add try statement for possible API errors
        result = (
            self.sheets.values()
            .get(spreadsheetId=file_id, range=f"{sheet_name}!{start_range}:{end_range}")
            .execute()
        )
        values = result.get("values", [])
        return values

    def collect_config(self):
        """
        Iterate through all yaml files in self.config_dir and store referenced
        sheet ranges.
        """
        config_files = SheetCollector.get_yaml_files(self.config_dir)
        for yaml_file in config_files:
            # Open yaml file as read
            with open(yaml_file, "r") as f:
                # create a key in yaml_data with the name of the
                # file and loaded data
                self.yaml_data[yaml_file.stem] = yaml.safe_load(f)

    def collect_sheets(self):
        """
        Iterate through the collected config, submit API
        requests and store results.
        """
        if not self.sheets:
            raise Exception("ERROR: Collector was not authenticated")
        for file_name, file_dict in self.yaml_data.items():
            write_path = file_dict["output_path"]
            source_id = file_dict["source_id"]
            self.sheets_data[file_name] = {}
            for sheet in file_dict["sheets"]:
                retrieved_data = self.get_sheet(
                    source_id, sheet["name"], sheet["start"], sheet["end"]
                )
                self.sheets_data[file_name][sheet["name"]] = retrieved_data

    @staticmethod
    def get_yaml_files(directory: pathlib.Path):
        """
        Find all yaml files recursively in directory.

        Args:
            directory (pathlib.Path): directory to search in

        Returns:
            list of path objects: paths to all found yaml files
        """

        return directory.glob("*.yaml")


collector = SheetCollector()
collector.collect_config()
collector.authenticate()
collector.collect_sheets()
print(json.dumps(collector.sheets_data, indent=4))
