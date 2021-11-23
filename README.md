# GridGopher

![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)
![BuiltWith](https://img.shields.io/badge/Built%20With-Python-blue?style=flat-square&logo=python&logoColor=yellow)
![Actions Status](https://github.com/noorbuchi/GridGopher/workflows/Lint%20and%20Test/badge.svg)
[![codecov](https://codecov.io/gh/noorbuchi/GridGopher/branch/main/graph/badge.svg?token=02353FAN4W)](https://codecov.io/gh/noorbuchi/GridGopher)


GridGopher is a plugin friendly tool that allows users to connect collected data
from Google Sheets and GitHub issue trackers and pull requests. The tool
provides the basic API and encourages users to utilize it in their applications.

## Set Up

GridGopher uses Poetry to create a Python virtual environment and manage
dependencies. For more information about Poetry, check out [the
documentation](https://python-poetry.org/). To set up the tool for use, please
follow the steps outlined below:

**1- Install Poetry:**

Install poetry using the steps outlined
[here](https://python-poetry.org/docs/#installation). To verify that poetry was
installed successfully run the following:

```
poetry -V
```

The expected output is the version of Poetry installed.

**2- Install Python Dependencies:**

Once poetry has been installed successfully, clone or download the repository
and navigate to the root of the repository. Use the following command to install
all the dependencies used by GridGopher:

```
poetry install
```

This command might take some time to finish running. Once it's completed,
GridGopher is ready for use!

## Running the Tool

Write some stuff

## Plugin System

Write some stuff

## API

Write some stuff

## Other

Write some stuff

A placeholder repository for Allegheny College automated grade transfer tool

## Important Notes

- Values in the `.env` file must be surrounded by double quotation marks `"`
  otherwise, newline character `\n` will cause issues.

Expected Format:

```.evn
TYPE="service_account"
PROJECT_ID="value"
PRIVATE_KEY_ID="value"
PRIVATE_KEY="Value"
AUTH_URI="value"
TOKEN_URI="value"
AUTH_PROVIDER_X509_CERT_URL="value"
CLIENT_X509_CERT_URL="value"
```
