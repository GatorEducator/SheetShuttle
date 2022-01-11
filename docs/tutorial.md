# Getting Started with GridGopher

- [Getting Started with GridGopher](#getting-started-with-gridgopher)
  - [Setting Up and Running Your Plugin](#setting-up-and-running-your-plugin)
    - [Setup The Path and Plugin Name](#setup-the-path-and-plugin-name)
    - [Add a `run()` Function](#add-a-run-function)
    - [Importing from GridGopher](#importing-from-gridgopher)
  - [Using the Google Sheets API](#using-the-google-sheets-api)
    - [Ensure that All Authentication Variables are Available and Accessible](#ensure-that-all-authentication-variables-are-available-and-accessible)
    - [Share the Google Sheets file(s) with the created service account](#share-the-google-sheets-files-with-the-created-service-account)
    - [Write YAML configuration used to retrieved data](#write-yaml-configuration-used-to-retrieved-data)
    - [Call `sheet_collector` from the plugin](#call-sheet_collector-from-the-plugin)
  - [Using the GitHub API](#using-the-github-api)
    - [Add GitHub Access Token](#add-github-access-token)
    - [Write or Generate YAML Configuration](#write-or-generate-yaml-configuration)
    - [Call `GithubManager` from Your Plugin](#call-githubmanager-from-your-plugin)

GridGopher provides a simple infrastructure to interact with Google Sheets API
as well as GitHub API. It gives the user the ability to create custom plugins
that integrate with the tool's workflow. This tutorial will provide some
examples and code snippets to get started with GridGopher.

## Setting Up and Running Your Plugin

There are few requirements to be met before diving in developing your plugin,
the following tasks are important to make sure the GridGopher can find and run
your custom plugin:

### Setup The Path and Plugin Name

By default, GridGopher searches the `plugins` directory for the `default`
plugin named `default.py`. If you wish to run your own plugin, you can
create a Python file in any directory on your system. However, the directory
and name of the this Python file must be passed into GridGopher's CLI in
order to be detected. For example, if the plugin `my_plugin.py` was created
in `../projects/my_plugins/`, then the CLI argument for `plugin_name` would be
`my_plugin` (**Note** that `.py` is omitted) and the value of
`plugins_directory` argument would be `../projects/my_plugins/`

### Add a `run()` Function

GridGopher assumes that a `run()` function exists in your plugin which gets
called in order to execute your custom code. To prevent errors while loading
and running the plugin, this function signature is required for every
plugin.
<!-- TODO: update this once **kwargs are fully supported -->

```python
def run(sheets_keys_file, sheets_config_directory, **kwargs):
    # rest of your plugin code
```

`TODO: More information is needed here after full support is added`

### Importing from GridGopher

In order to use the functionalities in GridGopher's infrastructure, your
plugin should import the needed modules.

```python
   # If collecting data from Google Sheets, sheet_collector should be imported
   from gridgopher import sheet_collector
   # To manipulate collected data, pandas should also be imported
   import pandas as pd

    # If Working with GitHub, the following modules should also be imported
   from gridgopher import github_objects
   from github import Github
```

## Using the Google Sheets API

The `sheets_collector` module is responsible for retrieving data from Google
Sheets and organizing it in nested objects such as sheets, and regions. In order
to make API request calls, `sheets_collector` relies on user-written YAML
configuration that follow the structure specified in the [schemas
guidline](schemas.md#sheets-schema). In this section, the structure of the retrieved data is
discussed as well as the supported functions of the `sheets_collector` module.

### Ensure that All Authentication Variables are Available and Accessible

There are two main ways to provide Google Sheets authentication tokens to
GridGopher. The tokens are obtained after setting up a service account.
Authentication information can be stored in a `.json` file or as part of a
`.env` file. This process is discussed in [Google Sheets Service Account
section](../README.md) of the README file. Regardless of which approach is
used, the name of the file should be passed as a CLI argument to GridGopher

### Share the Google Sheets file(s) with the created service account

Before attempting to access the data in the Google Sheets file, the created
service account must have access to the file. To do that please follow
[these instructions](Google_API_Setup.md#sharing-a-file-with-the-service-account).

### Write YAML configuration used to retrieved data

`TODO: add and cite API References`

In this step, the user outlines the structure that data should be organized
after being collected from Google Sheets. Various objects are created and
store in different formats. This section concerns how configuration is
formatted and read, however, more information regarding what
each object supports are discussed in API references.
In general, each Google Sheets file requires it's own YAML configuration
file, so in the case that the user is reading multiple Google Sheet files,
there needs to be more than one YAML file in the configuration directory.
The example below shows configuration for one Google Sheets file and splits
it up into multiple sheets and regions.

```yaml
source_id: my_sheet_id
sheets:
    - name: sheet1
      regions:
      - name: grades
        start: A1
        end: L4
        contains_headers: true
      - name: expenses
        start: F5
        end: K12
        contains_headers: false
        headers:
            - Jan
            - Feb
            - Mar
            - Apr
            - May
            - Jun
    - name: sheet2
      regions:
      - name: some_data
        start: A1
        end: Z10
        contains_headers: true
```

Here is a general description of the keys listed in the configuration:

- `source_id`: The ID of the Google Sheet file should be pasted as this
  value, it's typically found between the `/d/` and `/edit` in the URL of the
  file. The pasted ID should not include the `/d/` and `/edit` when pasted
  into the configuration.
- `sheets`: this key should include a list of sheet objects with two main
  keys, the name of the sheet, and a list of regions to break it down into.
- The data inside each region is stored as a Pandas DataFrame

With that in mind, the above configuration does the following:

1. In general retrieve the data from the file with ID `my_sheet_id`
2. Create two regions from `sheet1`
   1. First region is named `grades`, where data bounded by cell `A1` and
     `L4` are stored with the first row of the data as headers.
   2. Second region is named `expenses` and it stores data bound by cell `F5`
     and `K12`. The headers of the data frame are custom and they're listed
     in the `headers` list.
3. Create one region from `sheet2` named `some_data` which is bound by `A1`
  and `Z10`

### Call `sheet_collector` from the plugin

Once all previous setup steps are completed, you can begin writing your
plugin and utilizing the infrastructure of GridGopher. A quick way to get
started is the simple code snippet below which initializes a `SheetCollector`
object and executes the configuration to retrieve and store data from Google
Sheets.

```python
from gridgopher import sheet_collector

my_collector = sheet_collector.SheetCollector()
my_collector.collect_files()
```

Note that initializing a `SheetCollector` object accepts the following
optional arguments:

- `key_file`: path to the file containing Google Sheets API authentication
tokens. The file can be either a `.env` or `.json` format. The default
value of this argument is `.env`.
- `sources_dir`: path to the directory containing all the YAML configuration
to be read. The default value is `config/sheet_sources`

Once `collect_files()` finishes running, `my_collector.sheets_data` instance
variable is populated with all the collected data. The variable is a
dictionary where sheet names are keys in the dictionary and the values are
corresponding `Sheet` objects.

## Using the GitHub API

Similar to using the Google Sheets API, the GitHub API relies on authentication
token as well as user written or plugin generated configuration to execute all
the requests. The following sections describe the needed steps to set up and use
the GitHub API.

### Add GitHub Access Token

### Write or Generate YAML Configuration

### Call `GithubManager` from Your Plugin
