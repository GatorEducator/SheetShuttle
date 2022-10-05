"""Define a program to parse a Google Sheets URL and extract a sheet id."""

def extract_id(url: str) -> str:
    """Extract a sheet ID from a Google Sheets URL."""
    url_segments = url.split('/')
    collect = False
    for segment in url_segments:
        if collect:
            return segment
        if segment == "d":
            collect = True

def main():
    """Define program shell to test grab_id function."""
    url = input("What's the URL to parse? ")
    sheet_id = extract_id(url)
    print(sheet_id)

if __name__ == "__main__":
    main()