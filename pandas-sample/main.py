import pandas as pd
import json

df = pd.read_excel('sample.xlsx')
print(df.head(3))
df.columns
print(df["Student Name"])

result = df.to_json(orient="records")
parsed = json.loads(result)
json_object = json.dumps(parsed, indent=4)  
[
    {
        "col 1": "a",
        "col 2": "b"
    },
    {
        "col 1": "c",
        "col 2": "d"
    }
]
with open("sample.json", "w") as outfile:
    outfile.write(json_object)