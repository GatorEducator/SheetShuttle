"""Test cases for sheet_collector Module."""

import json
import pandas as pd
import pathlib
import pickle

from gridgopher import sheet_collector


def test_region_initialize():
    my_dataframe = pd.DataFrame([["name", "class", "grade"], ["Noor", "2022", "94"]])
    my_region = sheet_collector.Region("lab1", "CMPCS101", "A1", "Z20", my_dataframe)
    assert my_region.region_name == "lab1"
    assert my_region.parent_sheet_name == "CMPCS101"
    assert my_region.full_name == "CMPCS101_lab1"
    assert len(my_region.data) == 2


def test_region_print(capfd):
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
    assert type(out_data.data) == pd.DataFrame


def test_sheet_initialize_empty_config():
    sample_config = {}
    my_sheet = sheet_collector.Sheet(sample_config, None)
    assert not my_sheet.api
    assert len(my_sheet.config) == 0
    # TODO: this will thrown an error when check_config_schema is implemented
    assert not my_sheet.regions


def test_print_sheet_empty(capfd):
    sample_config = {}
    my_sheet = sheet_collector.Sheet(sample_config, None)
    my_sheet.print_sheet()
    captured = capfd.readouterr()
    assert captured.out == """"""


def test_print_sheet_with_data(capfd):
    sample_config = {}
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


def test_sheet_initialize_correct_config():
    # TODO: implement me
    assert True


def test_check_config_schema():
    # TODO: implement me after function is completed
    # TODO: use parameterized testing and files for this
    assert True


def test_to_dataframe_no_error_with_headers():
    # TODO: implement me
    assert True


def test_to_dataframe_no_error_no_headers():
    # TODO: implement me
    assert True


def test_to_dataframe_throws_error():
    # TODO: implement me
    assert True


def test_to_dataframe_empty_input():
    # TODO: implement me
    assert True
