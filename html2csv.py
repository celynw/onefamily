#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

from bs4 import BeautifulSoup


def main(args: argparse.Namespace) -> None:
    # Read HTML table from file
    with args.input_path.open() as f:
        soup = BeautifulSoup(f, "html.parser")
    table = soup.find("table")

    # Write CSV file
    with args.output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        # Ignore the first row, it's a title and shouldn't be in the CSV
        for row in table.find_all("tr")[1:]:
            values = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
            # Don't print rows when we didn't find any data
            if len(values) == 0 or all(v == "" for v in values):
                continue
            writer.writerow(values)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
        Arguments parsed from the command-line.
    """
    parser = argparse.ArgumentParser(
        description="Convert HTML table to CSV",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input_path", type=Path, help="Path to input HTML file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to output CSV file. Defaults to input_path.csv",
        dest="output_path",
    )

    args = parser.parse_args()
    if args.output_path is None:
        args.output_path = args.input_path.with_suffix(".csv")

    return args


if __name__ == "__main__":
    main(parse_args())
