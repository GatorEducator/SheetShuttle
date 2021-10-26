# Changes to Data Retrieval Approach

## Config Files

- User should be able to create data regions from the same sheet
- Regions would have a name
- Contain headings (true or false)

New Schema:

```yaml
source_id: file id from URL
output_path: name of directory where will this data be saved to
# list of the sheets to read from
sheets:
    - name: sheet1
      regions:
        - name: region1_1
          start: A1
          end: C3
          contains_headers: true
        - name: region1_2
          start: F1
          end: J7
          contains_headers: false
          headers:
            - col1
            - col2
            - col3
    - name: sheet2
      regions:
        - name: region2_1
          start: A1
          end: C3
          contains_headers: true
        - name: region2_2
          start: F1
          end: J7
          contains_headers: false
          headers:
            - col1
            - col2
            - col3

```

## Setting up a default plugin

Data processing should be used as a default plugin that can be overwritten by
the user