# Welcome to Sheetshuttle

## Getting Started with SheetShuttle

* [Getting Started with SheetShuttle](#getting-started-with-sheetshuttle)
  * [Setting Up and Running Your Plugin](#setting-up-and-running-your-plugin)
    * [Setup The Path and Plugin Name](#setup-the-path-and-plugin-name)
    * [Add a `run()` Function](#add-a-run-function)
    * [Importing from SheetShuttle](#importing-from-sheetshuttle)
  * [Using the Google Sheets API](#using-the-google-sheets-api)
    * [Ensure that All Authentication Variables are Available and Accessible](#ensure-that-all-authentication-variables-are-available-and-accessible)
    * [Share the Google Sheets file(s) with the created service account](#share-the-google-sheets-files-with-the-created-service-account)
    * [Write YAML configuration used to retrieved data](#write-yaml-configuration-used-to-retrieved-data)
    * [Call `sheet_collector` from the plugin](#call-sheet_collector-from-the-plugin)
  * [Using the GitHub API](#using-the-github-api)
    * [Add GitHub Access Token](#add-github-access-token)
    * [Write or Generate YAML Configuration](#write-or-generate-yaml-configuration)
    * [Call `GithubManager` from Your Plugin](#call-githubmanager-from-your-plugin)

## About

    SheetShuttle provides a simple infrastructure to interact with Google Sheets API
    as well as GitHub API. It gives the user the ability to create custom plugins
    that integrate with the tool's workflow. This tutorial will provide some
    examples and code snippets to get started with SheetShuttle.

## Setting Up and Running Your Plugin

    There are few requirements to be met before diving in developing your plugin,
    the following tasks are important to make sure SheetShuttle can find and run
    your custom plugin:

### Setup The Path and Plugin Name

    By default, SheetShuttle searches the `plugins` directory for the `default`
    plugin named `default.py`. If you wish to run your own plugin, you can
    create a Python file in any directory on your system. However, the directory
    and name of the this Python file must be passed into SheetShuttle's CLI in
    order to be detected. For example, if the plugin `my_plugin.py` was created
    in `../projects/my_plugins/`, then the CLI argument for `plugin_name` would be
    `my_plugin` (**Note** that `.py` is omitted) and the value of
    `plugins_directory` argument would be `../projects/my_plugins/`

### Add a `run()` Function

    SheetShuttle assumes that a `run()` function exists in your plugin which gets
    called in order to execute your custom code. To prevent errors while loading
    and running the plugin, this function signature is required for every
    plugin.
<!-- TODO: update this once **kwargs are fully supported -->

    ```python
    def run(sheets_keys_file, sheets_config_directory, **kwargs):
        # rest of your plugin code
    ```

`TODO: More information is needed here after full support is added`

### Importing from SheetShuttle

    In order to use the functionalities in SheetShuttle's infrastructure, your
    plugin should import the needed modules.

    ```python
    # If collecting data from Google Sheets, sheet_collector should be imported
    from sheetshuttle import sheet_collector
    # To manipulate collected data, pandas should also be imported
    import pandas as pd

        # If Working with GitHub, the following modules should also be imported
    from sheetshuttle import github_interaction
    from github import Github
    ```

## Using the Google Sheets API

    The `sheets_collector` module is responsible for retrieving data from Google
    Sheets and organizing it in nested objects such as sheets, and regions. In order
    to make API request calls, `sheets_collector` relies on user-written YAML
    configuration that follow the structure specified in the [schemas
    guidline](schemas.md#sheets-schema). In this section, the structure of
    the retrieved data is discussed as well as the supported functions of
    the `sheets_collector` module.

### Ensure that All Authentication Variables are Available and Accessible

    There are two main ways to provide Google Sheets authentication tokens to
    SheetShuttle. The tokens are obtained after setting up a service account.
    Authentication information can be stored in a `.json` file or as part of a
    `.env` file. This process is discussed in [Google Sheets Service Account
    section](../README.md#google-sheets-service-account) of the README file.
    Regardless of which approach is used, the name of the file should be
    passed as a CLI argument to SheetShuttle

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

    * `source_id`: The ID of the Google Sheet file should be pasted as this
    value, it's typically found between the `/d/` and `/edit` in the URL of the
    file. The pasted ID should not include the `/d/` and `/edit` when pasted
    into the configuration.
    * `sheets`: this key should include a list of sheet objects with two main
    keys, the name of the sheet, and a list of regions to break it down into.
    * The data inside each region is stored as a Pandas DataFrame

    With that in mind, the above configuration does the following:

    1. In general retrieve the data from the file with ID `my_sheet_id`
    1. Create two regions from `sheet1`

    * First region is named `grades`, where data bounded by cell `A1` and
    `L4` are stored with the first row of the data as headers.
    * Second region is named `expenses` and it stores data bound by cell `F5`
    and `K12`. The headers of the data frame are custom and they're listed
    in the `headers` list.

    1. Create one region from `sheet2` named `some_data` which is bound by `A1`
    and `Z10`

### Call `sheet_collector` from the plugin

    Once all previous setup steps are completed, you can begin writing your
    plugin and utilizing the infrastructure of SheetShuttle. A quick way to get
    started is the simple code snippet below which initializes a `SheetCollector`
    object and executes the configuration to retrieve and store data from Google
    Sheets.

    ```python
    from sheetshuttle import sheet_collector

    my_collector = sheet_collector.SheetCollector()
    my_collector.collect_files()
    ```

    Note that initializing a `SheetCollector` object accepts the following
    optional arguments:

    * `key_file`: path to the file containing Google Sheets API authentication
    tokens. The file can be either a `.env` or `.json` format. The default
    value of this argument is `.env`.
    * `sources_dir`: path to the directory containing all the YAML configuration
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

    The [GitHub Access Token section](../README.md#github-access-token) in README
    discusses how to generate a GitHub token and make it accessible to SheetShuttle.
    Without the token, SheetShuttle will not be able to authenticate with the API and
    post entries such as issues, pull requests, or files.

### Write or Generate YAML Configuration

    GitHub interactions also uses YAML configuration to execute API requests and
    post entries to a GitHub repository. This configuration can be user written or
    automatically generated by your plugin. The configuration must follow the
    structure described in the [schemas
    guide](schemas.md#github-interactions-schema) but an example is also shown and
    explained below.

    The configuration should be structured as a list of Entry objects that contain
    the type of entry as well as the action to be done. Different entries support
    different actions and attributes in their structure. For more information,
    refer to the schemas guide.

    ```yaml
    # Create an issue
    # labels are optional
    - type: issue
    action: create
    repo: repo_org/repo_name
    title: some new issue
    body: test body
    labels:
        - label1
        - label2

    # update/comment on an issue
    # Number of issue to update must be used instead of title
    # New labels can be added
    - type: issue
    action: update
    repo: repo_org/repo_name
    number: 1
    body: test body
    labels:
        - label1
        - label2

    # Create a pull request
    # base is the name of branch to merge into
    # head is the name of branch to merge from
    - type: pull request
    action: create
    repo: repo_org/repo_name
    title: test create pull request
    body: Test pull request create
    base: main
    head: test_branch

    # Update/add comment on a pull request
    # Number of pull request is used instead of title
    - type: pull request
    action: update
    repo: repo_org/repo_name
    number: 2
    body: Test pull request create


    # Create a new file in a branch
    # the path must include the format of the file to be created
    - type: file
    action: create
    repo: repo_org/repo_name
    path: folder1/file2.txt
    content: hello world!
    branch: main
    commit_message: sample commit message

    # Append to an existing file
    # This action appends the new content to the old content of the file
    - type: file
    action: update
    repo: repo_org/repo_name
    path: folder1/file2.txt
    content: hello world!
    branch: main
    commit_message: sample commit message

    # Replace an existing file
    # This action completely erases the old content of the file
    # and replaces it with the new content
    - type: file
    action: replace
    repo: repo_org/repo_name
    path: folder1/file2.txt
    content: hello world!
    branch: main
    commit_message: sample commit message
    ```

### Call `GithubManager` from Your Plugin

    Once configuration has been written or automatically generated, a
    `GitHubManager` object can be initialized in your plugin to collect and parse
    the configuration. The object also supports the ability to post the entries. The
    code snippet below shows an example of how it can be used.

    ```python
    from sheetshuttle import github_interaction

    my_manager = github_interaction.GitHubManager()
    my_manager.collect_config()

# All collected entries can be posted at once

    my_manager.post_all()

# OR they can be posted individually by type

    my_manager.post_issues()
    my_manager.post_pull_requests()
    my_manager.post_files()
    ```

    Note that when initializing a `GitHubManager` object, two optional arguments can
    be accepted:

    * `key_file`: the path to the file containing the GitHub token. By default the
    the value of this argument is `.env` causing the manager to look for the token
    in environment variables. Tokens can be stored in `.json` files or as
    environment variables.
    * `sources_dir`: the path to the directory containing YAML configuration files
    for the `GitHubManager` object. All YAML files are collected and parsed to
    create corresponding Entry objects. By default, the value of this argument is
    `config/github_interactions`.
