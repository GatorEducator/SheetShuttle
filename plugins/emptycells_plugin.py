""""Standard empty plugin for SheetShuttle."""

# If collecting data from Google Sheets, sheet_collector should be imported
from sheetshuttle import github_interaction, sheet_collector, util
# To manipulate collected data, pandas should also be imported
import pandas as pd
import numpy as np
import yaml

# If Working with GitHub, the following modules should also be imported
from sheetshuttle import github_interaction
from github import Github
# This function is required
def run(sheets_keys_file, sheets_config_directory, gh_config_directory, **kwargs):
    """Standard run function."""
    my_collector = sheet_collector.SheetCollector(sources_dir=sheets_config_directory)
    my_collector.collect_files()
    used_config = my_collector.sheets_data["git_creative_config"]
    pass
