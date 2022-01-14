""""Default plugin for SheetShuttle."""

from sheetshuttle import github_objects
from sheetshuttle import sheet_collector

from github import Github

# import os


def run(sheets_keys_file, sheets_config_directory, **kwargs):
    """Standard run function."""
    print("hello from the default plugin")
    # print("Received Arguments: ")
    # print(f"sheets_keys_file: {sheets_keys_file}")
    # print(f"sheets_config_directory: {sheets_config_directory}")

    # g = Github("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")
    # repo = g.get_repo("AC-GopherBot/test-1")
