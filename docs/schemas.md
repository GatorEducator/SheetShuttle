# Config Schemas

The examples shown here demonstrate the schemas for configuration read by
GridGopher. In order for the tool to function with no errors, user written
configuration must follow the specified format.

- [Config Schemas](#config-schemas)
  - [Sheets Schema](#sheets-schema)
    - [Defining Objects](#defining-objects)
      - [Region Object](#region-object)
      - [Sheet Object](#sheet-object)
    - [Overall Structure](#overall-structure)
    - [JSON Schema Structure](#json-schema-structure)
  - [GitHub Interactions Schema](#github-interactions-schema)
    - [Issue Schema](#issue-schema)
    - [Pull Request Schema](#pull-request-schema)
    - [File Schema](#file-schema)

## Sheets Schema

Sheets schema describe the format for configuration found in the
`config/sheet_sources` directory, which are used to retrieve Google Sheet data.

### Defining Objects

There are two main nested object structures used in the Sheets schema.

#### Region Object

This is the simplest object that does not contain complex nested objects in it. It
has the following structure:

```yml
name: <string> name of the region to create
start: <string> cell to start from (eg. A1)
end: <string> cell to end at (eg. H12)
contains_headers: <boolean> if selected range contains headers in the first row
```

If `contains_headers` was set to `false`, another key must be provided. The new
key is called `headers` and the structure would look as follows:

```yml
name: <string> name of the region to create
start: <string> cell to start from (eg. A1)
end: <string> cell to end at (eg. H12)
contains_headers: <boolean> if selected range contains headers in the first row
headers: <list of strings> headers to be used
```

With the possible structures in mind, here are a couple of examples of how a
region object can look like:

**Example 1:**

```yml
name: grades
start: A1
end: L4
contains_headers: true
```

**Example 2:**

```yml
name: expenses
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
```

#### Sheet Object

The sheet object is one level above the region structure and it looks as follow:

```yml
name: <string> name of sheet to read from in Google Sheets
regions: <list of region object> Regions to create from the sheet
```

**Example:**

```yml
name: sheet1
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
```

### Overall Structure

The outermost keys of the configuration must contain only two keys as follows:

```yml
source_id: <string> ID of sheet to read
sheets: <list of sheet objects>
```

**Example:**

```yml
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

### JSON Schema Structure

This is the structure used to validate the configuration using `jsonschema`:

```json
{
    "type": "object",
    "properties": {
        "source_id": {"type": "string"},
        "sheets": {"type": "array", "items": {"$ref": "#/$defs/sheet"}},
    },
    "required": ["source_id", "sheets"],
    "$defs": {
        "region": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "start": {"type": "string"},
                "end": {"type": "string"},
                "contains_headers": {"type": "boolean"},
                "headers": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["name", "start", "end", "contains_headers"],
            "additionalProperties": false,
        },
        "sheet": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "sheets": {"type": "array", "items": {"$ref": "#/$defs/region"}},
            },
        },
    },
}
```

## GitHub Interactions Schema

This type of schema describes the structure of configurations found in the
`config/github_interactions` directory. This configuration is used to post
entries to Github such as issue trackers, pull requests, and files.

### Issue Schema

### Pull Request Schema

### File Schema
