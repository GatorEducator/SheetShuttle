"""
Set up object oriented structure for Google Sheet data retrieval
"""

import json

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from google.oauth2 import service_account


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetsCollector:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.sheets = None
        self.config = {}

    # TODO: add other instance variables

    # TODO: fix the default path to be of object path type
    # def read_config(self, config_file="config/sheets_collector.json"):
    #     """
    #     Read config file and store contents in config instance variable

    #     Args:
    #         config_file: path to config file, defaults to the sheets.json
    #     """
    #     with open(config_file, "r") as f:
    #         self.config = json.load(f)

    def authenticate(self, key_file="private/keys.json"):
        self.credentials = service_account.Credentials.from_service_account_file(
            key_file, scopes=SCOPES
        )
        self.service = build("sheets", "v4", credentials=self.credentials)
        self.sheets = self.service.spreadsheets()

    def get_sheet(self, sheet_id):
        result = (
            self.sheets.values()
            .get(spreadsheetId=sheet_id, range="Sheet1!A1:C3")
            .execute()
        )
        values = result.get("values", [])
        print(values)


collector = SheetsCollector()
collector.authenticate()
collector.get_sheet("1jBN-UhmwGr_zjj0pZ5J6Gci4JKlHaHmrcdG4YvsH608")
