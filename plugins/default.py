""""Default plugin for GridGopher."""

from gridgopher import sheet_collector

# import os


def run():
    """Standard run function."""
    # collector = sheet_collector.SheetCollector()
    print("hello from the default plugin")
    my_collector = sheet_collector.SheetCollector()
    my_collector.collect_files()
    my_collector.print_contents()
