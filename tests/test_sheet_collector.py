"""Test cases for sheet_collector Module."""

import json
import os
import pathlib
import pickle
import pytest
import yaml

import pandas as pd

from sheetshuttle import sheet_collector

from sheetshuttle import util


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
    assert isinstance(out_data.data, pd.DataFrame)


def test_sheet_check_config_schema_no_error(test_data):
    """Use the test_data fixture to check json schema validation."""
    passing_data = test_data["sheets_schema_test"]["passing"]
    for config in passing_data:
        sheet_collector.Sheet.check_config_schema(config)
    assert True


def test_sheet_check_config_schema_throws_error(test_data):
    """Use the test_data fixture to check json schema validation."""
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
    first_item = """******	 overall 	 ******
start range: A1
end range: Z20
|    | 0    | 1     | 2     |
|---:|:-----|:------|:------|
|  0 | name | class | grade |
|  1 | Noor | 2022  | 94    |
*********************************"""
    second_item = """******	 labs 	 ******
start range: A2
end range: H20
|    | 0    | 1    | 2    |
|---:|:-----|:-----|:-----|
|  0 | name | lab1 | lab2 |
|  1 | Noor | 100  | 94   |
*********************************
"""
    assert first_item in captured.out
    assert second_item in captured.out


def test_sheet_to_dataframe_no_error_with_headers():
    """Check that conversion to data frame using preset headers is done correctly."""
    data = [["name", "class", "age"], ["Noor", 2022, 21], ["Thomas", "2023", 21]]
    my_dataframe = sheet_collector.Sheet.to_dataframe(data, headers_in_data=True)
    assert list(my_dataframe["name"]) == ["Noor", "Thomas"]


def test_sheet_to_dataframe_no_error_no_headers():
    """Check that conversion to data frame without using preset headers is done correctly."""
    data = [["Noor", 2022, 21], ["Thomas", "2023", 21]]
    my_dataframe = sheet_collector.Sheet.to_dataframe(
        data, headers_in_data=False, headers=["name", "class", "age"]
    )
    assert list(my_dataframe["name"]) == ["Noor", "Thomas"]


def test_sheet_to_dataframe_throws_error():
    """Check that an error is thrown by to_dataframe when using headers.

    headerslist is empty."""

    data = [["name", "class", "age"], ["Noor", 2022, 21], ["Thomas", "2023", 21]]
    with pytest.raises(Exception):
        sheet_collector.Sheet.to_dataframe(data, headers_in_data=False)
    assert True


def test_sheet_to_dataframe_empty_input():
    """Check that error is thrown when passed data is empty."""
    data = []
    with pytest.raises(Exception):
        sheet_collector.Sheet.to_dataframe(data, headers_in_data=True)
    assert True


def test_sheet_to_dataframe_one_row_input():
    """Check that error is thrown when passed contains one row only."""
    data = [["Noor", "Thomas", "Yanqiao"]]
    with pytest.raises(Exception):
        sheet_collector.Sheet.to_dataframe(data, headers_in_data=True)
    assert True


@pytest.mark.webtest
def test_sheet_execute_sheet_call_no_error():
    """Call a test google sheet and assert that the values are as expected.

    Will be skipped if authentication environment variables don't exist."""
    # initialize with environment variables authentication
    try:
        my_sheet_collector = sheet_collector.SheetCollector()
    except sheet_collector.MissingAuthenticationVariable:
        pytest.skip("Sheets authentication environment variables not found")
    expected_data = [
        ["Name", "Class", "Lab1", "Lab2", "Lab3", "Average"],
        ["Noor", "2022", "94", "54", "34.65", "60.88333333"],
        ["Tommy", "2023", "96", "79", "64.99", "79.99666667"],
        ["Yanqiao", "2024", "99", "68", "23.64", "63.54666667"],
        ["Tugi", "2024", "100", "97", "56.001", "84.33366667"],
    ]
    api = my_sheet_collector.sheets
    data_from_call = sheet_collector.Sheet.execute_sheets_call(
        api, "1EwSGkK3seRzHh8XGKlaRrpRdDuOrNCeAele5q_YIN4Y", "sheet1", "B2", "G6"
    )
    assert data_from_call == expected_data
    # reverse ranges to check if anything changes
    reversed_range_data_from_call = sheet_collector.Sheet.execute_sheets_call(
        api, "1EwSGkK3seRzHh8XGKlaRrpRdDuOrNCeAele5q_YIN4Y", "sheet1", "G6", "B2"
    )
    assert reversed_range_data_from_call == expected_data


@pytest.mark.webtest
def test_sheet_execute_sheet_call_empty_return():
    """Call a test google sheet and assert that the values are empty.

    Will be skipped if authentication environment variables don't exist."""
    # initialize with environment variables authentication
    try:
        my_sheet_collector = sheet_collector.SheetCollector()
    except sheet_collector.MissingAuthenticationVariable:
        pytest.skip("Sheets authentication environment variables not found")
    api = my_sheet_collector.sheets
    data_from_call = sheet_collector.Sheet.execute_sheets_call(
        api, "1EwSGkK3seRzHh8XGKlaRrpRdDuOrNCeAele5q_YIN4Y", "sheet1", "Z12", "AA15"
    )
    assert len(data_from_call) == 0
    assert data_from_call == []


@pytest.mark.webtest
def test_sheet_execute_sheet_call_throws_error():
    """Call a test google sheet and assert that an error is thrown.

    Error is due to a sheet name that doesn't exist.
    Will be skipped if authentication environment variables don't exist."""
    # initialize with environment variables authentication
    try:
        my_sheet_collector = sheet_collector.SheetCollector()
    except sheet_collector.MissingAuthenticationVariable:
        pytest.skip("Sheets authentication environment variables not found")
    api = my_sheet_collector.sheets
    with pytest.raises(Exception):
        sheet_collector.Sheet.execute_sheets_call(
            api,
            "1EwSGkK3seRzHh8XGKlaRrpRdDuOrNCeAele5q_YIN4Y",
            "nonexistentSheet",
            "B2",
            "G6",
        )
    assert True


@pytest.mark.webtest
def test_sheet_collect_regions(test_data):
    """Assert that regions are collected correctly in a Sheet object.

    Can be skipped if authentication variables aren't available"""
    try:
        my_sheet_collector = sheet_collector.SheetCollector()
    except sheet_collector.MissingAuthenticationVariable:
        pytest.skip("Sheets authentication environment variables not found")
    api = my_sheet_collector.sheets
    sample_config = test_data["collect_regions_test"]["sample_config"]
    my_sheet = sheet_collector.Sheet(sample_config, api)
    my_sheet.collect_regions()
    regions_keys = [
        "sheet1_lab_grades",
        "sheet1_roster",
        "sheet1_overall_grades",
        "sheet2_lab_grades",
    ]
    for region_key in regions_keys:
        assert region_key in my_sheet.regions


@pytest.mark.webtest
def test_sheet_collector_authenticate_api_json(tmp_path):
    """Check that the sheets api can be authenticated successfully from json
    file.

        Can be skipped if needed environment variables are not set.
    """
    # get environment variables as a dictionary
    creds_dict = {}
    for env_var in sheet_collector.ENV_VAR_LIST:
        var_value = os.getenv(env_var)
        if not var_value:
            pytest.skip(
                f"Sheets authentication environment variable {env_var} not found. Skipping test"
            )
        creds_dict[env_var.lower()] = var_value

    temporary_directory = tmp_path / "keys_folder"
    temporary_directory.mkdir()
    temporary_json = temporary_directory / "keys.json"
    with open(temporary_json, "w+", encoding="utf-8") as writefile:
        json.dump(creds_dict, writefile)

    credentials, service, sheets = sheet_collector.SheetCollector.authenticate_api(
        str(temporary_json)
    )
    assert credentials
    assert service
    assert sheets


@pytest.mark.webtest
def test_sheet_collector_authenticate_api_env():
    """Check that the sheets api can be authenticated successfully from
    environment variables.

        Can be skipped if needed environment variables are not set.
    """
    for env_var in sheet_collector.ENV_VAR_LIST:
        var_value = os.getenv(env_var)
        if not var_value:
            pytest.skip(
                f"Sheets authentication environment variable {env_var} not found. Skipping test"
            )

    credentials, service, sheets = sheet_collector.SheetCollector.authenticate_api(
        ".env"
    )
    assert credentials
    assert service
    assert sheets


@pytest.mark.webtest
def test_sheet_collector_authenticate_api_throws_error():
    """Check that an error is thrown when a file other than .env and .json is
    used to authenticate the Sheets api.
    """
    with pytest.raises(Exception):
        sheet_collector.SheetCollector.authenticate_api(".yaml")


@pytest.mark.webtest
def test_sheet_collector_collect_files_throws_error():
    """Check that collect_files() throws an error when the api isn't
    authenticated.

    Can be skipped if environment variables isn't set."""
    try:
        my_collector = sheet_collector.SheetCollector()
    except sheet_collector.MissingAuthenticationVariable:
        pytest.skip("Sheets authentication environment variables not found")
    my_collector.sheets = None
    with pytest.raises(Exception):
        my_collector.collect_files()


def test_sheet_collector_collect_files_prints_output(tmpdir, test_data, capfd):
    """Check that a dictionary of Sheet objects is created correctly in collect_files()"""
    try:
        my_collector = sheet_collector.SheetCollector()
    except sheet_collector.MissingAuthenticationVariable:
        pytest.skip("Sheets authentication environment variables not found")

    # setting up temporary config files using test_data
    temporary_directory = tmpdir.mkdir("temp")
    temp_path = str(temporary_directory)
    for file_name, config_val in test_data["collect_files_test"]["temp_files"].items():
        with open(
            pathlib.Path(".") / temp_path / file_name, "w+", encoding="utf-8"
        ) as outfile:
            yaml.dump(config_val, outfile)
    # Initialize the sheet collector and collect the files from the temporary directory
    my_collector = sheet_collector.SheetCollector(sources_dir=temp_path)
    my_collector.collect_files()
    for sheet_key in test_data["collect_files_test"]["expected_keys"]:
        assert sheet_key in my_collector.sheets_data
    my_collector.print_contents()
    captured = capfd.readouterr()
    for print_item in test_data["collect_files_test"]["expected_print"]:
        assert print_item in captured.out
