""""Default plugin for SheetShuttle."""

from sheetshuttle import github_objects
from sheetshuttle import sheet_collector

from github import Github

# import os


def run(sheets_keys_file, sheets_config_directory, **kwargs):
    """Standard run function."""
    print("hello from the default plugin")
    print("Additional arguments")
    print(kwargs["args"])
