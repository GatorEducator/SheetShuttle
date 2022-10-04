""""Standard empty plugin for SheetShuttle."""

# If collecting data from Google Sheets, sheet_collector should be imported
from sheetshuttle import sheet_collector
# To manipulate collected data, pandas should also be imported
import pandas as pd
# If Working with GitHub, the following modules should also be imported
from sheetshuttle import github_interaction
from github import Github
# This function is required
def run(sheets_keys_file, sheets_config_directory, gh_config_directory, **kwargs):
    """Standard run function."""
    pass
