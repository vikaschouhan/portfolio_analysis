# portfolio_analysis
Some useful collection of scripts for asset price analysis and scraping them freely from various sources on the web.<br> A backtesting framework based on [backtrader](https://www.backtrader.com/) is also currently implemented and hooked on to some of those scripts for automated backtesting and filtering for techincal investing.

## LICENSE
This work is made available under the terms of Gnu General Public License v2 (Please check LICENSE file for details)

## Dependencies
- python3-distutils
- python3-pandas
- python3-openpyxl
- python3-easygui
- python3-backtrader
- python3-matplotlib
- python3-pil
- python3-pdf2image
- python3-numpy
- python3-pyfolio
- python3-scipy
- python3-contextlib2
- python3-colorama
- python3-bs4
- python3-url_normalize
- python3-sklearn
- python3-urllib3
- pythom3-mpl_finance
- python3-plotly
- python3-tabulate
- python3-selenium
- python3-selenium_wire
- python3-requests
- python3-pyvirtualdisplay

## Scripts
* **eq_scan_on_investing_dot_com.py** - Generates an investing.com compatible database of assets with bhavcopy data pulled from [BSE](https://www.bseindia.com) and [NSE](https://www.nseindia.com) and pulling information for each of them from investing.com.
* **scrape_public_token_from_zerodha_kite.py** - Scrape public token id from zerodha for your account. Authorization has to provided in form of 'LOGIN,PASSWORD,PIN'.
* **gen_csvs_technical_kite.py** - Pull asset data from zerodha kite platform. This requires the "public token id" mentioned in previous paragraph.
* **gen_csvs_technical.py** - Pull asset data from investing.com (freely available in chart form). No username or password required.
* **get_option_historical_nse.py** - Pull option chain data for a particular month (only current, next and next to next month supported) for a particular stock or index from [NSE](https://www.nseindia.com)
* **get_option_historical_nse.py** - Pull historical option data for a particular stock or index for current, next or next to next month.
