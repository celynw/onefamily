# OneFamily Price Visualisation

The top plot represents the unit price over time.

- Bid price is how much you would need if you bought a unit
- Sell price is how much you would receive if you sold a unit
- `... (corrected)` values are scaled by relative UK inflation since the start

The bottom plot represents the value you hold.

- `... fees` values are with a fees calculation performed, so if correct will represent real-world value
- `(corrected)` values are scaled by relative UK inflation since the start
- The black dotted line is the break-even point

## 1. Get CSV file

First go to https://secure.onefamily.com/fundprices/index.asp and search for your product.
Once you find it, go to that page and go to the price history by clicking on `Download Historic Price DataDownload historic price data in HTML`.

You need to turn this data into a CSV file with the headings, `Bid Price`, `Offer Price`, `Date`.
Date is of the format `DD/MM/YYYY`.

To make things easier there is a conversion script.
You can save the page as HTML, then run `html2csv.py`:

Usage example:

```bash
python html2csv.py FILENAME.html -o history.csv
```

Full usage:

> ```bash
> usage: html2csv.py [-h] [-o OUTPUT_PATH] input_path
>
> Convert HTML table to CSV
>
> positional arguments:
>   input_path            Path to input HTML file
>
> options:
>   -h, --help            show this help message and exit
>   -o OUTPUT_PATH, --output OUTPUT_PATH
>                         Path to output CSV file. Defaults to input_path.csv (default: None)
> ```

## 2. Plot prices

You'll need the CSV file you obtained in the previous step.
Also, track down the number of units you bought and the date you bought them.

Usage example:

```bash
python plot.py history.csv -u 420.69 -d 01/01/1970
``````

Full usage:

> ```bash
> usage: plot.py [-h] [-u UNITS] [-d DATE] input_path
>
> Convert HTML table to CSV
>
> positional arguments:
>   input_path            Input CSV file
>
> options:
>   -h, --help            show this help message and exit
>   -u UNITS, --units UNITS
>                         Number of units held (default: None)
>   -d DATE, --date DATE  Date when the units were held, in DD/MM/YYYY format (default: None)
> ```
