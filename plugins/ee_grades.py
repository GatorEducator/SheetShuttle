import numpy as np
import pandas as pd
from sheetshuttle import github_interaction, sheet_collector, util
import yaml

STANDARD_REPO_NAME = "sample_org/sample_template"
STANDARD_TITLE = "Automated Grade Update"
STANDARD_BODY = "Your final grade is:"
STANDARD_LABELS = ["SheetShuttle", "Automated Grading"]
CONFIG_WRITE_DIR = "config/"
CONFIG_WRITE_FILENAME = "ee_grader_gh_config.yml"


def run(sheets_keys_file, sheets_config_directory, gh_config_directory, **kwargs):
    my_collector = sheet_collector.SheetCollector(sources_dir=sheets_config_directory)
    my_collector.collect_files()
    # Update ee_plugin with the new indexing structure
    used_config = (
        my_collector.sheets_data["sample_config"].sheets["students"].regions["names"]
    )

    # Get our data frames
    # FIXME: issue with sheetshuttle: unable to fill empty fields to be NaN when
    # dataframe type is float, specifically when those fields are originally ''
    student_info = used_config.regions["Sheet1_students_info"].data
    ee_grades = used_config.regions["Sheet1_engineering_efforts"].data
    projects_grades = used_config.regions["Sheet1_projects"].data
    survey_grades = used_config.regions["Sheet1_surveys"].data
    exam_grades = used_config.regions["Sheet1_exams"].data
    participation_grades = used_config.regions["Sheet1_participation"].data

    # create a list of students
    students = {}
    grades_config = {}

    # Iterate through each row from every dataframe
    # !Note: assumes that all data frames have the same number of rows
    row_count = student_info.shape[0]
    for student_index in range(0, row_count):
        student_name = student_info.iloc[student_index]["Student Name"]
        student_email = student_info.iloc[student_index]["Student Email"]
        student_username = student_info.iloc[student_index]["Student GitHub"]
        current_student = Student(student_name, student_email, student_username)
        # !NOTE: this should be refactored
        # iterate through EE
        start_index = 0
        while start_index < len(ee_grades.iloc[student_index]):
            current_student.add_ee(
                ee_grades.iloc[student_index][start_index : start_index + 4]
            )
            start_index += 4
        # Iterate through projects
        start_index = 0
        while start_index < len(projects_grades.iloc[student_index]):
            current_student.add_project(
                projects_grades.iloc[student_index][start_index]
            )
            start_index += 1
        # Iterate through surveys
        start_index = 0
        while start_index < len(survey_grades.iloc[student_index]):
            current_student.add_survey(survey_grades.iloc[student_index][start_index])
            start_index += 1
        # Iterate through exams
        start_index = 0
        while start_index < len(exam_grades.iloc[student_index]):
            current_student.add_exam(exam_grades.iloc[student_index][start_index])
            start_index += 1
        # Add participation grades
        start_index = 0
        while start_index < len(participation_grades.iloc[student_index]):
            current_student.add_participation(
                participation_grades.iloc[student_index][start_index]
            )
            start_index += 1
        # Add the students object to the list
        students[student_name] = current_student
        grades_config[student_name] = current_student.generate_new_issue_config()
    # Print the final grades to the console
    for student_name, obj in students.items():
        print(f"{student_name}:\t {obj.get_grade()}")

    # Write the configuration list of values to a yaml file to be read later by
    # github interactions
    full_config_path = CONFIG_WRITE_DIR + CONFIG_WRITE_FILENAME
    with open(full_config_path, "w+", encoding="utf-8") as writefile:
        yaml.dump(list(grades_config.values()), writefile, Dumper=NoAliasDumper)

    # Initialize the github interaction object and prepare for posting to github
    my_manager = github_interaction.GithubManager(sources_dir=CONFIG_WRITE_DIR)
    my_manager.collect_config()

    # TODO: Uncoment this to post everything
    # my_manager.post_all()


# !NOTE: this is optional and is only used to ignore aliases and anchors when
# !writing to a yaml file
class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


class Student:
    def __init__(self, name: str, email: str, username: str) -> None:
        self.name = name
        self.email = email
        self.username = username
        self.grades = {
            "ee": {"num": 0, "sum": 0, "weight": 0.4},
            "projects": {"num": 0, "sum": 0, "weight": 0.15},
            "surveys": {"num": 0, "sum": 0, "weight": 0.15},
            "exams": [],
            "participation": {"grade": 0, "weight": 0.05},
        }

    def add_ee(self, grade_list):
        # TODO: account for Nan Values
        crit_prcnt = ((grade_list[1] + grade_list[2] + grade_list[3]) / 3) * 100
        ee_prcnt = (grade_list[0] + crit_prcnt) / 200
        self.grades["ee"]["sum"] += ee_prcnt
        self.grades["ee"]["num"] += 1

    def add_project(self, grade):
        # TODO: account for Nan Values
        self.grades["projects"]["sum"] += grade
        self.grades["projects"]["num"] += 1

    def add_survey(self, grade):
        # TODO: account for Nan Values
        self.grades["surveys"]["sum"] += grade
        self.grades["surveys"]["num"] += 1

    def add_exam(self, grade):
        # TODO: account for Nan Values
        self.grades["exams"].append(grade)

    def add_participation(self, grade):
        self.grades["participation"]["grade"] = grade

    def get_grade(self):
        ee_grade = (self.grades["ee"]["sum"] / self.grades["ee"]["num"]) * self.grades[
            "ee"
        ]["weight"]
        projects_grade = (
            self.grades["projects"]["sum"] / self.grades["projects"]["num"]
        ) * self.grades["projects"]["weight"]
        survey_grade = (
            self.grades["surveys"]["sum"] / self.grades["surveys"]["num"]
        ) * self.grades["surveys"]["weight"]
        # !Note: exam weights are here
        exams_grade = ((self.grades["exams"][0] / 100) * 0.1) + (
            (self.grades["exams"][1] / 100) * 0.15
        )
        participation_grade = (self.grades["participation"]["grade"] / 5) * self.grades[
            "participation"
        ]["weight"]
        final_grade = (
            ee_grade + projects_grade + survey_grade + exams_grade + participation_grade
        )
        return final_grade

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
