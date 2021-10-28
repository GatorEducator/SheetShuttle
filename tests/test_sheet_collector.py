"""Test cases for sheet_collector Module."""

import json
import pathlib
import pickle
import pytest

import pandas as pd

from gridgopher import sheet_collector


def test_region_initialize():
    """Check that a Region object is correctly initialized with instance variables."""
    my_dataframe = pd.DataFrame([["name", "class", "grade"], ["Noor", "2022", "94"]])
    my_region = sheet_collector.Region("lab1", "CMPCS101", "A1", "Z20", my_dataframe)
    assert my_region.region_name == "lab1"
    assert my_region.parent_sheet_name == "CMPCS101"
    assert my_region.full_name == "CMPCS101_lab1"
    assert len(my_region.data) == 2


def test_region_print(capfd):
    """Check that region object is printed correctly."""
    my_dataframe = pd.DataFrame([["name", "class", "grade"], ["Noor", "2022", "94"]])
    my_region = sheet_collector.Region("lab1", "CMPCS101", "A1", "Z20", my_dataframe)
    my_region.print_region()
    captured = capfd.readouterr()
    assert (
        captured.out
        == """start range: A1
end range: Z20
|    | 0    | 1     | 2     |
|---:|:-----|:------|:------|
|  0 | name | class | grade |
|  1 | Noor | 2022  | 94    |\n"""
    )


def test_region_to_json(tmpdir):
    """Use temporary directory to test regions storage as json file."""
    tempdir = tmpdir.mkdir("temp")
    temp_path = str(tempdir)
    my_dataframe = pd.DataFrame([["name", "class", "grade"], ["Noor", "2022", "94"]])
    my_region = sheet_collector.Region("lab1", "CMPCS101", "A1", "Z20", my_dataframe)
    my_region.region_to_json(temp_path)
    with open(
        pathlib.Path(".") / temp_path / "CMPCS101_lab1.json", "r", encoding="utf-8"
    ) as input_file:
        out_data = json.load(input_file)
    assert not len(out_data) == 0
    assert out_data == {
        "data": {
            "0": {"0": "name", "1": "class", "2": "grade"},
            "1": {"0": "Noor", "1": "2022", "2": "94"},
        },
        "end_range": "Z20",
        "full_name": "CMPCS101_lab1",
        "parent_name": "CMPCS101",
        "region_name": "lab1",
        "start_range": "A1",
    }


def test_region_to_pickle(tmpdir):
    """Use temporary directory to test regions storage as pickle file."""
    tempdir = tmpdir.mkdir("temp")
    temp_path = str(tempdir)
    my_dataframe = pd.DataFrame([["name", "class", "grade"], ["Noor", "2022", "94"]])
    my_region = sheet_collector.Region("lab1", "CMPCS101", "A1", "Z20", my_dataframe)
    my_region.region_to_pickle(temp_path)
    with open(pathlib.Path(".") / temp_path / "CMPCS101_lab1.pkl", "rb") as input_file:
        out_data = pickle.load(input_file)
    assert out_data.region_name == my_region.region_name
    assert out_data.parent_sheet_name == my_region.parent_sheet_name
    assert out_data.full_name == my_region.full_name
    assert out_data.start_range == my_region.start_range
    assert out_data.end_range == my_region.end_range
    # TODO: should probably check values in out_data
    assert isinstance(out_data.data, pd.DataFrame)


def test_sheet_check_config_schema_no_error(test_data):
    """Use the test_data fixture to check json schema validation."""
    # TODO: add more data to this test case
    passing_data = test_data["sheets_schema_test"]["passing"]
    for config in passing_data:
        sheet_collector.Sheet.check_config_schema(config)
    assert True


def test_sheet_check_config_schema_throws_error(test_data):
    """Use the test_data fixture to check json schema validation."""
    # TODO: add more data to this test case
    failing_data = test_data["sheets_schema_test"]["failing"]
    for config in failing_data:
        with pytest.raises(Exception):
            sheet_collector.Sheet.check_config_schema(config)
    assert True


def test_sheet_initialize_empty_config():
    """Check that initializing a sheet with empty config throws error."""
    sample_config = {}
    with pytest.raises(Exception):
        sheet_collector.Sheet(sample_config, None)


def test_sheet_initialize_correct_config(test_data):
    """Check that a Sheet object is correctly initialized with instance variables."""
    sample_config = test_data["sheets_schema_test"]["passing"][0]
    my_sheet = sheet_collector.Sheet(sample_config, None)
    assert not my_sheet.api
    assert not len(my_sheet.config) == 0
    assert not my_sheet.regions


def test_print_sheet_empty(capfd, test_data):
    """Check that sheets are printed correctly when no regions exist."""
    sample_config = test_data["sheets_schema_test"]["passing"][0]
    my_sheet = sheet_collector.Sheet(sample_config, None)
    my_sheet.print_sheet()
    captured = capfd.readouterr()
    assert captured.out == """"""


def test_print_sheet_with_data(capfd, test_data):
    """Check that sheets are printed correctly when regions data exist."""
    sample_config = test_data["sheets_schema_test"]["passing"][0]
    my_sheet = sheet_collector.Sheet(sample_config, None)
    first_data = pd.DataFrame([["name", "class", "grade"], ["Noor", "2022", "94"]])
    first_region = sheet_collector.Region(
        "overall", "CMPCS101", "A1", "Z20", first_data
    )
    second_data = pd.DataFrame([["name", "lab1", "lab2"], ["Noor", "100", "94"]])
    second_region = sheet_collector.Region("labs", "CMPCS102", "A2", "H20", second_data)
    my_sheet.regions = {"overall": first_region, "labs": second_region}
    assert my_sheet.get_region("overall") == first_region
    my_sheet.print_sheet()
    captured = capfd.readouterr()
    assert (
        captured.out
        == """******	 overall 	 ******
start range: A1
end range: Z20
|    | 0    | 1     | 2     |
|---:|:-----|:------|:------|
|  0 | name | class | grade |
|  1 | Noor | 2022  | 94    |
*********************************
******	 labs 	 ******
start range: A2
end range: H20
|    | 0    | 1    | 2    |
|---:|:-----|:-----|:-----|
|  0 | name | lab1 | lab2 |
|  1 | Noor | 100  | 94   |
*********************************
"""
    )


def test_to_dataframe_no_error_with_headers():
    """Check that conversion to data frame using preset headers is done correctly."""
    # TODO: implement me
    assert True


def test_to_dataframe_no_error_no_headers():
    """Check that conversion to data frame without using preset headers is done correctly."""
    # TODO: implement me
    assert True


def test_to_dataframe_throws_error():
    """Check that an error is thrown by to_dataframe when using headers.

    headerslist is empty."""
    # TODO: implement me
    assert True


def test_to_dataframe_empty_input():
    """Check that error is thrown when passed data is empty."""
    # TODO: implement me
    assert True
