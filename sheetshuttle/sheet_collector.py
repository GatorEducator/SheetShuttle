"""Set up object oriented structure for Google Sheet data retrieval."""

import json
import os
import pathlib
import pickle
from typing import Dict, List

import pandas as pd  # type: ignore[import]
import yaml
from google.oauth2 import service_account  # type: ignore[import]
from googleapiclient.discovery import build  # type: ignore[import]
from jsonschema import validate

from sheetshuttle import util

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "source_id": {"type": "string"},
        "sheets": {
            "type": "array",
            "items": {"$ref": "#/$defs/sheet"},
            "minItems": 1,
        },
    },
    "required": ["source_id", "sheets"],
    "$defs": {
        "region": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "start": {"type": "string"},
                "end": {"type": "string"},
                "contains_headers": {"type": "boolean"},
                "headers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
                "fill": {"type": "boolean"},
                "types": {
                    "anyOf": [
                        {
                            "type": "string",
                            "enum": [
                                "object",
                                "string",
                                "int",
                                "float",
                                "bool",
                                "datetime",
                            ],
                        },
                        {
                            "type": "object",
                            "additionalProperties": {
                                "type": "string",
                                "enum": [
                                    "object",
                                    "string",
                                    "int",
                                    "float",
                                    "bool",
                                    "datetime",
                                ],
                            },
                        },
                    ]
                },
            },
            "required": ["name", "start", "end", "contains_headers"],
            "if": {"properties": {"contains_headers": {"const": False}}},
            "then": {
                "required": ["headers"],
            },
        },
        "sheet": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "regions": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/region"},
                    "minItems": 1,
                },
            },
            "required": ["name", "regions"],
        },
    },
}

ENV_VAR_LIST = [
    "TYPE",
    "PROJECT_ID",
    "PRIVATE_KEY_ID",
    "PRIVATE_KEY",
    "CLIENT_EMAIL",
    "CLIENT_ID",
    "AUTH_URI",
    "TOKEN_URI",
    "AUTH_PROVIDER_X509_CERT_URL",
    "CLIENT_X509_CERT_URL",
]


class MissingAuthenticationVariable(Exception):
    """Raised when a Sheets authentication variable is missing."""


class SheetCollector:
    """Authenticate Sheets api and store retrieved data."""

    def __init__(self, key_file=".env", sources_dir="config/sheet_sources") -> None:
        """
        Create a SheetCollector object that stores a dictionary of sheets.

        Uses the yaml files in the config/sheet_sources directory.

        Args:
            key_file (str, optional): path to Google Sheets API user keys and
            tokens. Defaults to ".env".

            sources_dir (str, optional): path to where the configuration
            is stored. Defaults to "config/sheet_sources"
        """
        self.key_file: str = key_file
        (
            self.credentials,
            self.service,
            self.sheets,
        ) = SheetCollector.authenticate_api(self.key_file)
        self.config_dir = pathlib.Path(sources_dir)
        self.sheets_data: Dict[str, Sheet] = {}

    def print_contents(self) -> None:
        """Print all Sheet objects in self.sheets_data."""
        for sheet in self.sheets_data.values():
            sheet.print_sheet()

    def collect_files(self) -> None:
        """
        Update sheets_data with Sheet objects from Google Sheets.

        Requires that the API was authenticated successfully.

        Raises:
            Exception: thrown when the Google Sheets API is not authenticated.
        """
        if not self.sheets:
            raise Exception("ERROR: Collector was not authenticated")
        # get a list of all yaml and yml path objects in the config_dir
        config_files: List[pathlib.Path] = util.get_yaml_files(self.config_dir)
        if not config_files:
            raise Exception(f"ERROR: No configuration files found in {self.config_dir}")
        for yaml_file in config_files:
            # Open yaml file as read
            with open(yaml_file, "r", encoding="utf-8") as config_file:
                config_data = yaml.safe_load(config_file)
                # create sheet object using the yaml data
                sheet_obj = Sheet(config_data, self.sheets)
                # fill the sheet object with the regions
                # by excecuting API calls
                sheet_obj.collect_regions()
                # store the sheet object in sheet_data, use the yaml file name
                # as key
                self.sheets_data[yaml_file.stem] = sheet_obj

    @staticmethod
    def authenticate_api(key_file):
        """Use credentials from key_file our environment authenticate access to a service account.

        Args:
            key_file (str, optional): Path to file containing API tokens.
                Can be either JSON or .env file
        """
        creds_dict = {}
        # Retreive the credentials
        if key_file.endswith(".json"):
            try:
                with open(key_file, "r", encoding="utf-8") as input_file:
                    creds_dict = json.load(input_file)
            except FileNotFoundError as error_obj:
                print(
                    f"ERROR: file {key_file} not found, credentials could not be collected."
                )
                raise error_obj
            # validate that only the needed keys are in the dictionary
            keys_to_remove = []
            lower_case_vars = map(lambda x: x.lower(), ENV_VAR_LIST)
            for variable_name in creds_dict.keys():
                # remove any extra values from the dictionary if they exist
                if variable_name not in lower_case_vars:
                    keys_to_remove.append(variable_name)
            for removable_key in keys_to_remove:
                creds_dict.pop(removable_key)
            diff = set(lower_case_vars).difference(set(creds_dict.keys()))
            if not len(diff) == 0:
                raise MissingAuthenticationVariable(
                    f"Variables {diff} could not be found"
                )
        elif key_file.endswith(".env"):
            for env_var in ENV_VAR_LIST:
                var_value = os.getenv(env_var)
                if not var_value:
                    raise MissingAuthenticationVariable(
                        f"Variable {env_var} could not be found"
                    )
                creds_dict[env_var.lower()] = var_value
        else:
            raise Exception(
                f"Unclear source of Sheets authentication keys {key_file}."
                + "Must be a .env or .json file"
            )
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES
        )
        service = build("sheets", "v4", credentials=credentials)
        # pylint: disable=E1101
        sheets = service.spreadsheets()
        return credentials, service, sheets


class Sheet:
    """Retrieve Google Sheets data and store as Regions."""

    def __init__(self, config: Dict, sheets_api) -> None:
        """Initialize a Sheet object.

        Args:
            config (Dict): a dictionary containing file
                sheets file retrieval configuration
            sheets_api: authenticated sheets api object
        """
        self.api = sheets_api
        self.config: Dict = config
        Sheet.check_config_schema(self.config)
        self.regions: Dict[str, Region] = {}

    def collect_regions(self):
        """Iterate through configuration and request data through API."""
        for sheet in self.config["sheets"]:
            for region in sheet["regions"]:
                region_data = Sheet.execute_sheets_call(
                    self.api,
                    self.config["source_id"],
                    sheet["name"],
                    region["start"],
                    region["end"],
                )
                if "fill" in region and region["fill"]:
                    # Find region dimensions
                    columns, rows = util.calculate_dimensions(
                        region["start"], region["end"]
                    )
                    region_data = util.fill_to_dimensions(region_data, columns, rows)
                # set the default type as string
                types = "string"
                if "types" in region:
                    types = region["types"]
                if region["contains_headers"]:
                    data = Sheet.to_dataframe(region_data, types=types)
                else:
                    data = Sheet.to_dataframe(
                        region_data,
                        headers_in_data=False,
                        headers=region["headers"],
                        types=types,
                    )
                region_object = Region(
                    region["name"],
                    sheet["name"],
                    region["start"],
                    region["end"],
                    data,
                )
                self.regions[region_object.full_name] = region_object

    def get_region(self, region_name: str):
        """Return a region object from the regions dictionary.

        Args:
            region_name (str): name of the region to get

        Returns:
            Region: the region object from the self.regions dictionary
        """
        requested_region: Region = self.regions[region_name]
        return requested_region

    def print_sheet(self):
        """Iterate through self.regions and print the contents."""
        for region_id, region in self.regions.items():
            print(f"******\t {region_id} \t ******")
            region.print_region()
            print("*********************************")

    @staticmethod
    def to_dataframe(
        data: List[List], headers_in_data=True, headers=None, types="string"
    ) -> pd.DataFrame:
        """Convert the data from Sheets API from List[List] pandas dataframe.

        Args:
            data (List[List]): Retrieved data from Sheets API
            headers_in_data (bool, optional): Is column headers included in the
                data. Defaults to True.
            headers (list, optional): If column headers are not included, use
            the headers in this list. Defaults to [].
            types (string or dict): one pandas datatype for the whole dataframe
                or a dictionary with column labels and their data types.
                Defaults to string.

        Raises:
            Exception: thrown when headers is empty and headers_in_data
            is False
            Exception: thrown when data is empty
            Exception: thrown when less than two rows of data exists and
                headers_in_data is True

        Returns:
            pd.DataFrame: The pandas dataframe after resulting from the data
        """
        if not data:
            raise Exception("ERROR: empty data cannot be converted to dataframe")
        if headers_in_data:
            # if data contains headers, there must be at least 2 rows
            if len(data) < 2:
                raise Exception(
                    "ERROR: data must contain at least two rows if headers are in data."
                )
            result_data = pd.DataFrame(data[1:], columns=data[0]).astype(types)
            return result_data
        if not headers:
            raise Exception("No passed table headers")
        result_data = pd.DataFrame(data, columns=headers).astype(types)
        return result_data

    @staticmethod
    def check_config_schema(config: Dict):
        """Validate the yaml configuration against a preset schema.add().

        Args:
            config (Dict): the configuration to validate

        Raises:
            ValidationError: The schema doesn't validate agains the preset
            json schema
        """
        validate(instance=config, schema=CONFIG_SCHEMA)

    @staticmethod
    def execute_sheets_call(
        api, file_id: str, sheet_name: str, start_range: str, end_range: str
    ) -> list[list]:
        """Execute an API call to get google sheets data.

        Args:
            file_id (str): ID of the Google Sheet file
            sheet_name (str): Name of the sheet in the file
            start_range (str): Cell name to start from (eg. A4)
            end_range (str): Cell name to end at (eg. H5)

        Returns:
            list[list]: the data in the specified range.
        """
        return (
            api.values()
            .get(
                spreadsheetId=file_id,
                range=f"{sheet_name}!{start_range}:{end_range}",
            )
            .execute()
            .get("values", [])
        )


class Region:
    """Store data frame and metadata about Google Sheet region."""

    # pylint: disable=R0913
    def __init__(
        self,
        region_name: str,
        parent_sheet_name: str,
        start_range: str,
        end_range: str,
        data: pd.DataFrame,
    ) -> None:
        """Create a Region object.

        Args:
            region_name (str): name of the region
            parent_sheet_name (str): name of the sheet the region belongs to
            start_range (str): Cell name to start from (eg. A4)
            end_range (str): Cell name to end at (eg. H5)
            data (pd.DataFrame): Data in the region
        """
        self.region_name = region_name
        self.parent_sheet_name = parent_sheet_name
        self.full_name = f"{parent_sheet_name}_{region_name}"
        self.start_range = start_range
        self.end_range = end_range
        self.data: pd.DataFrame = data

    def print_region(self):
        """Print the contents of the region in a markdown table format."""
        print(f"start range: {self.start_range}")
        print(f"end range: {self.end_range}")
        print(self.data.to_markdown())

    def region_to_pickle(self, directory: pathlib.PosixPath):
        """Write the region object to a Pickle file.

        Args:
            directory (pathlib.PosixPath): path to the directory where the file
                be stored
        """
        with open(
            pathlib.Path(".") / directory / f"{self.full_name}.pkl", "wb"
        ) as outfile:
            pickle.dump(self, outfile)

    def region_to_json(self, directory: pathlib.PosixPath):
        """Write the region object to a JSON file.

        Args:
            directory (pathlib.PosixPath): path to the directory where the file
                be stored
        """
        self_data = {
            "region_name": self.region_name,
            "parent_name": self.parent_sheet_name,
            "full_name": self.full_name,
            "start_range": self.start_range,
            "end_range": self.end_range,
            "data": self.data.to_dict("index"),
        }
        with open(
            pathlib.Path(".") / directory / f"{self.full_name}.json",
            "w+",
            encoding="utf-8",
        ) as outfile:
            json.dump(self_data, outfile, indent=4)
