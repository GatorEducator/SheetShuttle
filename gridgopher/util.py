"""Include general utility functions to avoid code replication."""

import os
import pathlib
from typing import List

GH_ENV_VAR_NAME = "GH_ACCESS_TOKEN"


def get_yaml_files(path_obj):
    """Get a list of .yaml and .yml files in the path."""
    extensions = ["*.yaml", "*.yml"]
    config_files: List[pathlib.Path] = list(path_obj.glob(extensions[0]))
    config_files.extend(list(path_obj.glob(extensions[1])))
    return config_files


def gh_token_exists() -> bool:
    """Check if a github token doesn't exist in the environment."""
    token = os.getenv(GH_ENV_VAR_NAME)
    if not token:
        return True
    return False
