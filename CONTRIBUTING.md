# Contributing Guidelines

Thank you for taking the time to contribute to SheetShuttle! This guide will
help you to effectively get started and contribute to the project.

## Table of Contents

- [Contributing Guidelines](#contributing-guidelines)
  - [Table of Contents](#table-of-contents)
  - [Raising an Issue](#raising-an-issue)
  - [Making a Pull Request](#making-a-pull-request)
  - [Project Standards](#project-standards)
    - [Development Environment](#development-environment)
    - [Automated Testing](#automated-testing)
    - [Test Coverage](#test-coverage)
    - [Code Linting](#code-linting)

## Raising an Issue

If you have a new issue to raise, first check the [Issue
Tracker](https://github.com/GatorEducator/SheetShuttle/issues)
to ensure someone has not already raised it. Select whether your
issue is a bug report or a feature request. Please follow the provided
template and use as much detail as possible when describing your issue.
For bug reports, it is important to provide steps to replicate the bug
and to provide all system information as well as the Python version
being used.

## Making a Pull Request

The development team uses the GitHub Flow Model to guide our engineering of this tool and we invite you to also follow it as you make a contribution. If you have a new feature or bug fix that you want the project maintainers to merge into SheetShuttle, then you should make a pull request. Please follow the provided template when you are describing your pull request, bearing in mind that the project maintainers will not merge any pull requests that either do not adhere to the template or break any aspects of the automated build. You should read the following subsection to learn more about the project standards to which all of SheetShuttle's contributors adhere.

## Project Standards

### Development Environment

If you want to participate in the development of GatorGrader, the project maintainers suggest the installation of the latest Python release. In addition to installing Git to access the project's GitHub repository, you should also install Poetry for its support of package and virtual environment management. The project's maintainers do not require the use of a specific text editor on integrated development environment. Once you have installed Git and Poetry you can type the following command in your terminal window to clone SheetShuttle's GitHub repository:

```
git clone git@github.com:GatorEducator/SheetShuttle.git
```

If you are not already a member of SheetShuttle's development team, then we suggest that you fork its GitHub repository and use it for the work that you intend to contribute. If you plan to develop new features for SheetShuttle then you will want to run the tool's test suite as well as other tasks with Poetry. Therefore, you will need to type `poetry install`.

### Automated Testing

The developers use Pytest for testing SheetShuttle. If you want to run the test suite to see if the test cases are passing, then you can type this command into the terminal window.

```bash
poetry run task test
```

### Test Coverage

Along with running the test suite, the developers of SheetShuttle use statement and branch coverage to inform their testing activities. Please make sure that you maintain 100% statement and branch coverage as you add new features or introduce bug fixes. If it is not possible for you to maintain complete statement and branch coverage, please document the circumstances in your pull request. To see the coverage of the tests while also highlighting the lines that are not currently covered by the tests, you can type this command in a terminal window.

```bash
poetry run task coverage
```

### Code Linting

The developers of SheetShuttle use linting and code formatting tools such as Pylint, Pydocstyle, Flake8 and Black. Please make sure that the source code in your pull request fully adheres to the project's coding standard as enforced by all of the automated linting tools. If it is not possible for you to maintain compliance with the checks made by these tools, then please document the circumstances in your pull request. If you have installed SheetShuttle's development dependencies with Poetry, you can run all of the linters by typing this command in a terminal window.

```bash
poetry run task lint
```

Please note that if any linter fails the rest of them will not run. Because of this, the command should be run until no linting errors are produced.
