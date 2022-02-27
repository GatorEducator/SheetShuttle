from pprint import pprint

import numpy as np
import pandas as pd
from sheetshuttle import github_objects, sheet_collector, util


def run(sheets_keys_file, sheets_config_directory, **kwargs):
    print("Running EE grading plugin...")
    # Initialize collector
    my_collector = sheet_collector.SheetCollector(sources_dir=sheets_config_directory)
    my_collector.collect_files()
    # Get and concatenate the data
    my_sheet = my_collector.sheets_data["sample_config"]
    names_region = my_sheet.regions["Sheet1_names"]
    effort1_region = my_sheet.regions["Sheet1_EE"]
    full_df = pd.concat(
        [names_region.data, effort1_region.data],
        axis=1,
    )
    grades = {}
    # Iterate through the rows
    for index, row in full_df.iterrows():
        # Initialize a student with their name
        student_name = row[0]
        current_student = Student(student_name)
        start_index = 1
        while start_index < len(row):
            # !NOTE: Skip this assignment if overall eval is empty
            if np.isnan(row[start_index]):
                start_index += 4
                continue
            # Add the information of this assignment assuming that it has 4 columns
            current_student.add_assignment(
                row[start_index],
                row[start_index + 1],
                row[start_index + 2],
                row[start_index + 3],
            )
            start_index += 4
        # Calculate the current student's grade
        grades[current_student.name] = current_student.get_grade()

    pprint(grades)


class Student:
    def __init__(self, name: str) -> None:
        self.name = name
        self.ee_num = 0
        self.current_sum = 0.0

    def add_assignment(self, full_eval, crit1, crit2, crit3):
        crit_prcnt = ((crit1 + crit2 + crit3) / 3) * 100
        ee_prcnt = (full_eval + crit_prcnt) / 200
        self.current_sum += ee_prcnt
        self.ee_num += 1

    def get_grade(self, weight=0.3):
        return self.current_sum / self.ee_num * weight
