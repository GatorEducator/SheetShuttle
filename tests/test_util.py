"""Test cases for util Module."""

from sheetshuttle import util


def test_fill_to_dimensions_appends_None_to_empty_strings():
    """Check that blank cells are type None."""
    # input data with empty strings as empty cells
    input_data = [
        ["col1", "col2", "col3", "col4"],
        ["fizz", "", "fooz", "fizz2"],
        ["buzz", "fooz2", "buzz2", ""]
    ]

    # expected data with None as empty cells
    expected_data = [
        ["col1", "col2", "col3", "col4"],
        ["fizz", None, "fooz", "fizz2"],
        ["buzz", "fooz2", "buzz2", None]
    ]

    # append None where there is a mismatch in data and number of columns/rows
    new_data = util.fill_to_dimensions(input_data, 4, 3)

    # check to see if empty elements get None
    assert new_data == expected_data


def test_fill_to_dimensions_appends_None_to_col_mismatch():
    """Check that column missing from input is added."""
    # input data with 3 columns
    input_data = [
        ["col1", "col2", "col3"],
        ["fizz", "fooz", "fizz2"],
        ["buzz", "fooz2", "buzz2"]
    ]

    # expected data with 4 columns
    expected_data = [
        ["col1", "col2", "col3", None],
        ["fizz", "fooz", "fizz2", None],
        ["buzz", "fooz2", "buzz2", None]
    ]

    # append None where there is a mismatch in data and number of columns/rows
    new_data = util.fill_to_dimensions(input_data, 4, 3)

    # check to see if 4th column of None is appended
    assert new_data == expected_data


def test_fill_to_dimensions_appends_None_to_row_mismatch():
    """Check that row missing from input is added."""
    # input data with 2 rows
    input_data = [
        ["col1", "col2", "col3", "col4"],
        ["buzz", "fooz2", "buzz2", "bizz"]
    ]

    # expected data with 3 rows
    expected_data = [
        ["col1", "col2", "col3", "col4"],
        ["buzz", "fooz2", "buzz2", "bizz"],
        [None, None, None, None]
    ]

    # append None where there is a mismatch in data and number of columns/rows
    new_data = util.fill_to_dimensions(input_data, 4, 3)

    # check to see if 3rd row of None is appended
    assert new_data == expected_data
