from pprint import pprint

import numpy as np
import pandas as pd
from sheetshuttle import github_interaction, sheet_collector, util
import yaml

STANDARD_REPO_NAME = "sample_org/sample_template"
STANDARD_TITLE = "Automated Grade Update"
STANDARD_BODY = "Current engineering effort grade is:"
STANDARD_LABELS = ["SheetShuttle", "Automated Grading"]
CONFIG_WRITE_DIR = "config/"
CONFIG_WRITE_FILENAME = "ee_grader_gh_config.yml"


def run(sheets_keys_file, sheets_config_directory, **kwargs):
    print("Running EE grading plugin...")
    # Initialize collector
    print("fetching data from Google Sheets...")
    my_collector = sheet_collector.SheetCollector(sources_dir=sheets_config_directory)
    my_collector.collect_files()
    # Get and concatenate the data
    print("Calculating grades...")
    my_sheet = my_collector.sheets_data["sample_config"]
    names_region = my_sheet.regions["Sheet1_names"]
    effort1_region = my_sheet.regions["Sheet1_EE"]
    full_df = pd.concat(
        [names_region.data, effort1_region.data],
        axis=1,
    )
    grades_config = {}
    # Iterate through the rows
    for index, row in full_df.iterrows():
        # Initialize a student with their name
        student_name = row[0]
        current_student = Student(student_name, f"{student_name}_uname")
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
        # Store configuration in a dictionary
        grades_config[student_name] = current_student.generate_new_issue_config()

    # Write the configuration list of values to a yaml file to be read later by
    # github interactions
    print("Creating Github Configuration...")
    full_config_path = CONFIG_WRITE_DIR + CONFIG_WRITE_FILENAME
    with open(full_config_path, "w+", encoding="utf-8") as writefile:
        yaml.dump(list(grades_config.values()), writefile, Dumper=NoAliasDumper)

    print("Posting to Github...")
    # Initialize the github interaction object and prepare for posting to github
    my_manager = github_interaction.GithubManager(sources_dir=CONFIG_WRITE_DIR)
    my_manager.collect_config()

    # TODO: Uncoment this to post everything
    # my_manager.post_all()

    print("Done!")


# !NOTE: this is optional and is only used to ignore aliases and anchors when
# !writing to a yaml file
class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


class Student:
    def __init__(self, name: str, username: str) -> None:
        self.name = name
        self.username = username
        self.ee_num = 0
        self.current_sum = 0.0

    def add_assignment(self, full_eval, crit1, crit2, crit3):
        crit_prcnt = ((crit1 + crit2 + crit3) / 3) * 100
        ee_prcnt = (full_eval + crit_prcnt) / 200
        self.current_sum += ee_prcnt
        self.ee_num += 1

    def get_grade(self, weight=0.3):
        return self.current_sum / self.ee_num * weight

    def generate_new_issue_config(self):
        config = {
            "type": "issue",
            "action": "create",
            "repo": f"{STANDARD_REPO_NAME}_{self.username}",
            "title": f"{self.name} {STANDARD_TITLE}",
            "body": f"{STANDARD_BODY} {self.get_grade()}",
            "labels": STANDARD_LABELS,
        }
        return config
