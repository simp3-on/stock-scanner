# tickers.py
import pandas as pd
import requests
from io import StringIO

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_column(df, possible_cols):
    """
    Returns the first matching column from possible_cols.
    """
    for col in possible_cols:
        if col in df.columns:
            return df[col]
    raise KeyError(f"No matching column found in {df.columns}")

def get_us_tickers():
    """
    Returns a dictionary of {symbol: company_name} for S&P 500.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url, headers=HEADERS)
    df = pd.read_html(StringIO(response.text), header=0)[0]

    symbol_col = get_column(df, ["Symbol", "Ticker"])
    name_col = get_column(df, ["Security", "Company"])

    return {symbol_col[i].strip(): name_col[i].strip() for i in range(len(symbol_col))}

def get_eu_tickers():
    """
    Returns a dictionary of {symbol: company_name} for Euro Stoxx 50, DAX 40, FTSE 100.
    Adds yfinance-compatible suffixes to symbols.
    """
    tickers = {}

    sources = [
        ("https://en.wikipedia.org/wiki/Euro_Stoxx_50", ".EU", ["Ticker", "Ticker symbol", "Symbol"], ["Company", "Name"]),
        ("https://en.wikipedia.org/wiki/DAX", ".DE", ["Ticker", "Ticker symbol", "Symbol"], ["Company", "Name"]),
        ("https://en.wikipedia.org/wiki/FTSE_100_Index", ".L", ["EPIC", "Ticker", "Symbol"], ["Company", "Name"])
    ]

    for url, suffix, symbol_cols, name_cols in sources:
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                print(f"Failed fetching {url}: HTTP {response.status_code}")
                continue

            df = pd.read_html(StringIO(response.text), header=0)[0]

            # If table has numeric columns, fallback to first column for symbol and second for name
            if all(isinstance(c, int) for c in df.columns):
                symbols = df.iloc[:, 0]
                names = df.iloc[:, 1] if df.shape[1] > 1 else ["N/A"] * len(df)
            else:
                symbols = get_column(df, symbol_cols)
                try:
                    names = get_column(df, name_cols)
                except KeyError:
                    names = ["N/A"] * len(symbols)

            for i, s in enumerate(symbols):
                tickers[s.strip() + suffix] = names[i].strip() if i < len(names) else "N/A"

        except Exception as e:
            print(f"Error processing {url}: {e}")

    return tickers
