import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose", help="increase output verbosity", action="store_true"
    )


if __name__ == "__main__":
    main()
