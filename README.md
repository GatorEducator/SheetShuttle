# SheetShuttle

![License](https://img.shields.io/badge/license-MIT-blue?style=flat)
![BuiltWith](https://img.shields.io/badge/Built%20With-Python-blue?style=flat&logo=python&logoColor=yellow)
![Actions Status](https://github.com/noorbuchi/SheetShuttle/workflows/Lint%20and%20Test/badge.svg)
[![codecov](https://codecov.io/gh/noorbuchi/SheetShuttle/branch/main/graph/badge.svg?token=02353FAN4W)](https://codecov.io/gh/noorbuchi/SheetShuttle)
![stars](https://img.shields.io/github/stars/noorbuchi/SheetShuttle.svg)

![SheetShuttleLogo](images/Logo.png)

SheetShuttle is a plugin friendly tool that connects Google Sheets
and GitHub by allowing the user to post collected data to issue trackers, pull
requests, and files. The tool
provides and object oriented API and encourages users to utilize it in their
applications.

- [SheetShuttle](#sheetshuttle)
  - [Set Up and Installation](#set-up-and-installation)
    - [Recommended Installation Using `pip`](#recommended-installation-using-pip)
    - [Manually Building SheetShuttle](#manually-building-sheetshuttle)
  - [Running SheetShuttle](#running-sheetshuttle)
    - [API Setup](#api-setup)
      - [Google Sheets Service Account](#google-sheets-service-account)
      - [Github Access Token](#github-access-token)
    - [Writing Config](#writing-config)
      - [Sheets Collector](#sheets-collector)
      - [Github Interactions](#github-interactions)
    - [Using Command Line Interface](#using-command-line-interface)
      - [Initialize a New Plugin](#initialize-a-new-plugin)
      - [Running an Existing Plugin](#running-an-existing-plugin)
    - [Plugin System](#plugin-system)

## Set Up and Installation

### Recommended Installation Using `pip`

SheetShuttle can be installed using Python's package manager `pip`. By running
the following command, SheetShuttle and all its dependencies are installed.

```shell
pip install sheetshuttle
```

Using this command to install SheetShuttle will ensure that you have the latest
most stable version of the tool. Additionally, you will be able to run the tool
anywhere on your system using the `sheetshuttle` command.

### Manually Building SheetShuttle

To get the latest changes from `main` or other development branches, make sure
to clone the project's repository and follow these steps to create Python
virtual environment, install dependencies, and build the tool.

SheetShuttle uses Poetry to create a Python virtual environment and manage
dependencies. For more information about Poetry, check out [the
documentation](https://python-poetry.org/). To set up the tool for use, please
follow the steps outlined below:

**1- Install Poetry:**

Install Poetry using the steps outlined
[here](https://python-poetry.org/docs/#installation). To verify that Poetry was
installed successfully run the following:

```shell
poetry -V
```

The expected output is the version of Poetry installed.

**2- Install Python Dependencies:**

Once Poetry has been installed successfully, clone or download the repository
and navigate to the root of the repository. Use the following command to install
all the dependencies used by SheetShuttle:

```shell
poetry install
```

This command might take some time to finish running. Once it is completed,
SheetShuttle is ready for use!

**3- Build SheetShuttle or Run Using Poetry:**

After the development environment is ready, you can build an installable `.whl`
file using `poetry build` command, or continue to use the tool by running
`poetry run sheetshuttle` from the project directory and passing any additional CLI arguments.

## Running SheetShuttle

For a thorough steps refer to this [tutorial](docs/tutorial.md)

### API Setup

SheetShuttle requires authentication tokens for a Google Sheets API service
account. A GitHub access token is also needed if some features are used. To set
up a service account and get the tokens, please follow the steps below:

#### Google Sheets Service Account

[This tutorial](https://youtu.be/4ssigWmExak?t=215)
from `3:35` until `8:20` gives clear and
detailed steps on how to create a service account and create an authentication
key. However, it includes extra steps that not everyone will need to follow. You
can follow the video if preferred or the [Sheets API
Guide](docs/Google_API_Setup.md).

Once API credentials have been downloaded, there are 2 ways to allow SheetShuttle
to use them.

1. Place the downloaded JSON file in the root of the project repository
1. OR create a new `.env` file and transfer the information from the `.json`
   file to the environment file in the following format.

**Important Note:** Values in the `.env` file must be surrounded
by double quotation marks `"` otherwise, newline character `\n`
will cause issues.

Note that variable names must be in upper case.

```.evn
TYPE="value"
PROJECT_ID="value"
PRIVATE_KEY_ID="value"
PRIVATE_KEY="value"
CLIENT_EMAIL="value"
CLIENT_ID="value"
AUTH_URI="value"
TOKEN_URI="value"
AUTH_PROVIDER_X509_CERT_URL="value"
CLIENT_X509_CERT_URL="value"
```

#### Github Access Token

If you intend to use SheetShuttle's GitHub interactions features, it is
required to create a GitHub access token and place it correctly in
the project repository. To create a token, please use the official
guide found
[here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
The created token should be granted `repo` access.

Once a token has been created, there are two ways to allow SheetShuttle
to use it:

1. Create a json file in the repository root with the following format (note
   that the `gh_access_token` key is required):

   ```json
   {
     "gh_access_token": "paste your token here"
   }
   ```

1. OR add a variable to the `.env` file in the following format

     ```.env
     GH_ACCESS_TOKEN="paste your token here"
     ```

### Writing Config

SheetShuttle relies on user written YAML configuration to
collect data from Google Sheets and organize it in regions.
GitHub interactions are also managed by
YAML configuration. To read more about the structure of SheetShuttle
configuration, please refer to our [schema documentation](docs/schemas.md).

#### Sheets Collector

Sheets Collector is the component of SheetShuttle that is responsible
for making Google Sheets API calls and retrieving data from user
specified files and sheets. Additionally, it creates an object
oriented structure for regions and sheets of data.
In order to use this component, configuration YAML files are needed
in the `config/sheet_sources` directory. Multiple files can be used if multiple
sheets are being read at the same time.

#### Github Interactions

Another component of SheetShuttle is the GitHub Interaction interface. It is
responsible for making API requests to GitHub and posting user specified
information to GitHub in the form of issue trackers, ull requests, and files.
The user has complete control of this component's behavior through YAML
configuration files found in `config/github_interactions` directory. Multiple
files can be used if preferred.

### Using Command Line Interface

After installing SheetShuttle using `pip`, the command `sheetshuttle` becomes
available to run the tool from any location on your system. To get help on the
CLI commands for SheetShuttle, you can always run `sheetshuttle --help` to get
the available options. This section gives additional details on the available
subcommands for the tool.

#### Initialize a New Plugin

To make the process of creating a new plugin more convenient and less error
prone, the `init` command will create a plugin template that
fulfils the structural requirement.

```shell
sheetshuttle init my_plugin_name
```

This command creates a Python file named `my_plugin_name.py` in the same
directory the command was ran in. This file can then be edited and used as the
plugin for SheetShuttle.

#### Running an Existing Plugin

The `run` command is responsible for executing a user defined plugin. It
supports a help message that displays all the available arguments and their
description. Some of these arguments are required while others are optional.
Additionally, most of them already hold a default value that gets used when no
value is passed through the command.

```shell
$ sheetshuttle run --help

Usage: sheetshuttle run [OPTIONS]

  Run sheetshuttle using your custom plugin.

Options:
  -kf, --sheets-keys-file TEXT    Path to the Sheets api keys, either .json or
                                  .env file  [default: .env]

  -sd, --sheets-config-directory TEXT
                                  Directory to get the sheets configuration
                                  .yaml files from  [default:
                                  config/sheet_sources/]

  -gd, --gh-config-directory TEXT
                                  Directory to get the Github configuration
                                  .yaml files from  [default:
                                  config/gh_sources/]

  -pd, --plugins-directory TEXT   Directory to get plugins from  [default:
                                  plugins/]

  -pn, --plugin-name TEXT         Name of plugin to use for processing
                                  [default: default]

  -ja, --json-args TEXT           Path to the JSON file with additional
                                  arguments. [Optional]

  --help                          Show this message and exit.

```

### Plugin System

SheetShuttle supports user defined plugins that use the API provided by the
tool. These plugins typically follow a specific format where they must contain a
`run` function. When the directory and name of the plugin are provided in the
`sheetshuttle run` command, the plugin is validated and then immediately ran.
