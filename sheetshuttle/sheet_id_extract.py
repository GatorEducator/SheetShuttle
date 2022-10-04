"""Define a program to parse a Google Sheets URL and extract a sheet id."""

# Tokens assumed to *always* denote the start and end of a Google Sheets sheet id
start_token = "/d/"
end_token = "/"

def grab_id(url: str) -> str:
    """Extract a sheet id from a Google Sheets URL."""
    sheet_id = ""
    token_characters_verified = 0
    for i in range(len(url)):
        # Start token and end tokens both verified
        if token_characters_verified > len(start_token):
            break
        # Start token fully verified...
        elif token_characters_verified == len(start_token):
            # ...and end token first encountered
            if url[i] == end_token:
                token_characters_verified += 1
            # ...and end token not yet encountered (character "capture" condition)
            else:
                sheet_id += url[i]
        # URL character matches start token character
        elif url[i] == start_token[token_characters_verified]:
            token_characters_verified += 1
        # Start token interrupted, or URL character not part of start token
        else:
            token_characters_verified = 0
    return sheet_id

def main():
    """Define program shell to test grab_id function."""
    url = input("What's the URL to parse? ")
    sheet_id = grab_id(url)
    print(sheet_id)

if __name__ == "__main__":
    main()