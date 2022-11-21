""""Default plugin for SheetShuttle."""

from pathlib import Path
from typing import List

from sheetshuttle import github_objects
from sheetshuttle import sheet_collector


def run(
    sheets_keys_file: str, sheets_config: List[Path], gh_config: List[Path], **kwargs
):
    """Standard run function."""
    print("hello from the default plugin")
    print(f"sheets_keys_file: {sheets_keys_file}")
    print(f"sheets_config: {sheets_config}")
    print(f"gh_config: {gh_config}")
    print(f"Additional arguments {kwargs}")
    my_collector = sheet_collector.SheetCollector(sheets_config, sheets_keys_file)
    my_collector.collect_files()
