"""Include general utility functions to avoid code replication."""

import os
import pathlib
from typing import List, Tuple, Any

from openpyxl.utils.cell import coordinate_from_string, column_index_from_string


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


def calculate_dimensions(start_range: str, end_range: str) -> Tuple[int, int]:
    """Calculate region dimensions (columns, rows) using the start and end ranges.

    Args:
        start_range (str): the start range, example: H12
        end_range (str): the end range, example L20

    Returns:
        Tuple[int, int]: dimensions of the region. (number of columns,
        number df rows )
    """
    # Split the range into letter, number Tuple
    start_data = coordinate_from_string(start_range)
    end_data = coordinate_from_string(end_range)
    # Convert letters into numbers and store them back
    start_dimensions = (column_index_from_string(start_data[0]), start_data[1])
    end_dimensions = (column_index_from_string(end_data[0]), end_data[1])
    # Subtract start from end to find the dimensions
    range_dimensions = (
        end_dimensions[0] - start_dimensions[0] + 1,
        end_dimensions[1] - start_dimensions[1] + 1,
    )
    return range_dimensions


def fill_to_dimensions(
    data: List[List[Any]], columns: int, rows: int
) -> List[List[Any]]:
    """Append None where there is a mismatch in the data and the dimensions.

    Args:
        data (List[List[str]]): data to fill
        columns (int): number of expected columns
        rows (int): number of expected rows

    Returns:
        List[List[str]]: data after fill
    """
    # Make sure that the length of a row equals number of columns
    for row in data:
        value_nums = len(row)
        # mismatch found
        if value_nums < columns:
            # Add the difference in None values
            col_difference = columns - value_nums
            row.extend([None] * col_difference)
    # check that the correct number of rows is present
    if len(data) < rows:
        row_difference = rows - len(data)
        for _ in range(0, row_difference):
            data.append([None] * columns)

    return data
