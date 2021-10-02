# Name Placeholder (open to suggestions!)

## General Purpose

The general idea behind this tool is to create a simple way to post students
grades from Google Sheet into a pull request/issue tracker in a GitHub
repository. In order to facilitate the implementation and testing of this tool,
it will be split up into smaller
components that perform tasks independently. While the different components will
run in a pipeline fashion, it could be possible to run some in parallel.

## Design

The different components of this tool are:

- **Central Command**: The role of this component is to parse user arguments and
  direct the flow of the tool as needed. It will implement the command line
  interface and handle any errors with user input. Additionally, it will read "secrets"
  such as the authentication tokens from a separate configuration file and pass
  them to other components.
- **Data Retrieval**: The responsibility of this component is to read the user
  provided data present in Google Sheets and return it in the form of a Pandas
  data frame. In order to complete its tasks, the component must have access to
  user tokens and secret API keys to successfully authenticate with Google's
  API.
- **Data Processing**: This component will contain all the logic needed to
  calculate each student's grade using the retrieved Pandas data frame. It will
  utilize a user provided configuration file to determine data columns to
  read and the weight of each data point in the calculation of the grade.
- **Report Producer**: Once grades have been calculated, this component will be
  used to generate a report in the form of markdown text that gives the student
  details about their grade. Aspects such as missing assignments, incomplete
  labs, and test scores should be included. (Optional: it would be cool to use
  markdown badges that change colors to display this information. Example: grade
  between 0-60 => red badge, 70-80 => orange, 80-90 => yellow, 90-100 => green).
- **GitHub Poster**: This step can run somewhat in parallel to the report
  producer. Once a student's report is completed, this component uses the GitHub
  API to post the report to an issue tracker/pull request. Similar to data
  retrieval, this component will need to authenticate with the GitHub API.
  Additionally, it's important to make sure that it has access to the private
  organization and repositories will the grades will be posted.

## Packages and Tools

- Python
- Pipenv/poetry (whichever is preferred)
- Pandas
- Pytest (and possibly other pytest plugins)
- PyGitHub
- Google API packages: google-api-python-client, google-auth-httplib2, google-auth-oauthlib
- Package to generate the report: (Forgot the name)

## Testing

It's very important to ensure that the components of the tool are working as
intended. Additionally, making sure that the tool can be set up and ran on a
variety of platform is another aspect of testing.

### Unit Tests

These tests will involve the smallest parts of the tool (functions and
components). They will be ran using Pytest and its powerful features such as
parameterized testing and code coverage. Unit tests should be developed along
with the tool's core functionalities instead of leaving them to the very end.
It will be challenging to test some components that rely on Google and Github's
API, and the plan for that is still in progress.

### Continuos Integration Tests (CIT)

The focus of these tests is to ensure that the tool and its dependencies can be
installed and ran on multiple platforms (Mac, Linux, and Windows). Github
Actions will be used to set up and run CITs and a build indicator will show the
status of the build. Additionally, Unit tests, code coverage test, linting, and
other tests may be ran as part of the build to ensure that submitted code is up
to standard.
