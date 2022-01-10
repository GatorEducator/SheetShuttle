"""Test the main module of GridGopher"""
import pytest

from gridgopher import main


@pytest.mark.parametrize(
    "directory,name,errors",
    [
        ("plugins/", "default", False),
        ("plugins/", "non_existent_plugin", True),
        ("non_existent_directory/", "default", True),
        ("non_existent_directory/", "non_existent_plugin", True),
    ],
)
def test_load_plugin(directory, name, errors):
    """Check that existing plugins can be loaded successfully.

    And incorrect plugins throw errors.
    """
    if errors:
        with pytest.raises(Exception):
            main.load_plugin(directory, name)
    else:
        main.load_plugin(directory, name)
