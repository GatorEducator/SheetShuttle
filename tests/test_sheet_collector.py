"""
Test cases for SheetsCollector Module
"""

from src import sheets_collector


def test_read_config():
    collector = sheets_collector.SheetsCollector()
    collector.read_config()
    assert collector.config == {"name": "noor buchi"}
