"""Include general utility functions to avoid code replication."""

import pathlib
from typing import List


def get_yaml_files(path_obj):
    """Get a list of .yaml and .yml files in the path."""
    extensions = ["*.yaml", "*.yml"]
    config_files: List[pathlib.Path] = list(path_obj.glob(extensions[0]))
    config_files.extend(list(path_obj.glob(extensions[1])))
    return config_files
