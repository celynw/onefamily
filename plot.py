#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main(args: argparse.Namespace, inflation: dict[int, float]) -> None:
    args.units = 0 if args.units is None else args.units
    args.date = datetime(list(inflation.keys())[-1], 1, 1) if args.date is None else args.date

    # Read CSV file to DataFrame
    # The columns will be: Bid Price, Offer Price, Date
    data = pd.read_csv(args.input_path, index_col="Date")
    data.index = pd.to_datetime(data.index)

    # Get inflation multipliers for the range
    inflation = {year: rate for year, rate in inflation.items() if year > data.index.year.min()}
    inflated = {}
    value = 1.0
    for year, rate in inflation.items():
        value /= 1 + rate
        inflated[year] = value
    inflated[data.index.year.min() - 1] = 1.0
    inflated = dict(sorted(inflated.items()))

    # If units and date are specified, calculate the price and add as a column
    # Exact buy date probably doesn't exist in the index. If not, use the previous date
    date = args.date if args.date in data.index else data.index[data.index < args.date][-1]

    # Add a column which:
    # - data is empty before `date`
    # - At and after `date`, is the current Bid Price multiplied by args.units
    column = data["Bid Price"].copy()
    column.loc[:date] = None
    column.loc[date:] *= args.units
    data["Sell Price"] = column

    buy_price = data["Offer Price"].loc[date] * args.units

    # Drop ALL rows outside the range of the data
    data = data.dropna()

    data["Sell Price fees"] = data["Sell Price"].copy()
    # Each year in January, subtract fees from "Sell Price"
    accrued = 0
    last_year_taken = None
    for date, row in data.iterrows():
        if date.month == 1 and date.year != last_year_taken:
            last_year_taken = date.year
            accrued += row["Sell Price fees"] * 0.01  # 1%
            accrued += 6  # Assuming it's 6 every year, all I know is it was 6 in 2021
        data["Sell Price fees"].loc[date] = row["Sell Price fees"] - accrued

    print(f"Premiums paid to date: {accrued:.2f}")

    # Apply inflation
    for year, multiplier in inflated.items():
        for col in ["Bid Price", "Offer Price", "Sell Price", "Sell Price fees"]:
            data.loc[data.index.year == year, f"{col} (corrected)"] = (
                data.loc[data.index.year == year, col] * multiplier
            )

    # Drop ALL rows outside the range of the data
    data = data.dropna()

    print(f"Interest accrued: {data['Sell Price'].iloc[-1] - buy_price:.2f}")
    print(f"Corrected interest accrued: {data['Sell Price (corrected)'].iloc[-1] - buy_price:.2f}")
    # Print interest rate of those
    relative_interest = (data["Sell Price"].iloc[-1] - buy_price) / buy_price
    duration = (data.index[-1] - data.index[0]).days / 365
    print(f"Interest rate: {relative_interest / duration:.2%}")
    # Print rate with fees into account
    relative_interest = (data["Sell Price fees"].iloc[-1] - buy_price) / buy_price
    print(f"Interest rate (fees): {relative_interest / duration:.2%}")
    # Print corrected interest rate
    relative_interest = (data["Sell Price (corrected)"].iloc[-1] - buy_price) / buy_price
    print(f"Corrected interest rate: {relative_interest / duration:.2%}")
    # Print corrected interest rate with fees into account
    relative_interest = (data["Sell Price fees (corrected)"].iloc[-1] - buy_price) / buy_price
    print(f"Corrected interest rate (fees): {relative_interest / duration:.2%}")

    # Two plots
    _, axes = plt.subplots(2, 1, sharex=True)
    axes = axes

    # Plot markets
    data[["Bid Price", "Offer Price", "Bid Price (corrected)", "Offer Price (corrected)"]].plot(ax=axes[0])

    # Plot held value
    # data[["Sell Price", "Sell Price (corrected)"]].plot(ax=axes[1])
    data[["Sell Price", "Sell Price fees", "Sell Price (corrected)", "Sell Price fees (corrected)"]].plot(ax=axes[1])
    # Draw a horizontal line at buy_price
    axes[1].axhline(buy_price, color="k", linestyle="--")

    plt.show()


# https://www.worlddata.info/europe/united-kingdom/inflation-rates.php
inflation = {
    2022: 7.92,
    2021: 2.52,
    2020: 0.99,
    2019: 1.74,
    2018: 2.29,
    2017: 2.56,
    2016: 1.01,
    2015: 0.37,
    2014: 1.45,
    2013: 2.29,
    2012: 2.57,
    2011: 3.86,
    2010: 2.49,
    2009: 1.96,
    2008: 3.52,
    2007: 2.39,
    2006: 2.46,
    2005: 2.09,
    2004: 1.39,
    2003: 1.38,
    2002: 1.52,
    2001: 1.53,
    2000: 1.18,
    1999: 1.75,
    1998: 1.82,
    1997: 2.20,
    1996: 2.85,
    1995: 2.70,
    1994: 2.22,
    1993: 2.56,
    1992: 4.59,
    1991: 7.46,
    1990: 8.06,
    1989: 5.76,
    1988: 4.16,
    1987: 4.15,
    1986: 3.43,
    1985: 6.07,
    1984: 4.96,
    1983: 4.61,
    1982: 8.60,
    1981: 11.88,
    1980: 17.97,
    1979: 13.42,
    1978: 8.26,
    1977: 15.84,
    1976: 16.56,
    1975: 24.21,
    1974: 16.04,
    1973: 9.20,
    1972: 7.07,
    1971: 9.44,
    1970: 6.37,
    1969: 5.45,
    1968: 4.70,
    1967: 2.48,
    1966: 3.91,
    1965: 4.77,
    1964: 3.28,
    1963: 2.02,
    1962: 4.20,
    1961: 3.45,
    1960: 1.00,
}
inflation = {year: rate / 100 for year, rate in inflation.items()}
# Sort keys
inflation = dict(sorted(inflation.items()))


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
    parser.add_argument("input_path", type=Path, help="Input CSV file")
    parser.add_argument("-u", "--units", type=float, help="Number of units held")
    parser.add_argument("-d", "--date", type=str, help="Date when the units were held, in DD/MM/YYYY format")

    args = parser.parse_args()

    # If only one of units or date is specified, raise an error
    if (args.units is None) ^ (args.date is None):
        parser.error("If units or date are specified, both must be specified")
    if args.date is not None:
        args.date = pd.to_datetime(args.date, format="%d/%m/%Y")

    return args


if __name__ == "__main__":
    main(parse_args(), inflation)
