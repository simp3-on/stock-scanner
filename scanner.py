import yfinance as yf
from tickers import get_us_tickers, get_eu_tickers

def scan_market(market="US", relaxed=False):
    """
    Fast stock scanner with company names.
    Uses batch yf.download(), skips market cap.
    """
    results = []
    # Fetch tickers as {symbol: name}
    ticker_dict = get_us_tickers() if market == "US" else get_eu_tickers()
    ticker_list = list(ticker_dict.keys())
    if not ticker_list:
        return results
    # Fetch last 2 days of data for all tickers in batch
    try:
        data = yf.download(ticker_list, period="2d", group_by="ticker", threads=True, progress=False)
    except Exception as e:
        print(f"Error downloading data: {e}")
        return results
    for symbol in ticker_list:
        try:
            if symbol not in data.columns.get_level_values(0):
                continue
            hist = data[symbol] if len(ticker_list) > 1 else data
            if len(hist) < 2:
                continue
            latest = hist.iloc[-1]
            previous = hist.iloc[-2]
            price = latest["Close"]
            prev_price = previous["Close"]
            price_change = price - prev_price
            percent_change = (price_change / prev_price) * 100
            volume = latest["Volume"]
            avg_volume = hist["Volume"].mean()
            relative_volume = volume / avg_volume
            open_price = latest["Open"]
            high = latest["High"]
            low = latest["Low"]
            # Filters
            if relaxed:
                min_change = 1 if market == "US" else 0.5
                min_rvol = 1 if market == "US" else 0.5
                min_vol = 100_000 if market == "US" else 50_000
            else:
                min_change = 3
                min_rvol = 1.5
                min_vol = 500_000
            if (
                abs(percent_change) >= min_change and
                relative_volume >= min_rvol and
                10 <= price <= 500 and
                volume >= min_vol
            ):
                results.append({
                    "symbol": symbol,
                    "name": ticker_dict.get(symbol, "N/A"),
                    "price": round(price, 2),
                    "percent_change": round(percent_change, 2),
                    "price_change": round(price_change, 2),
                    "open": round(open_price, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "volume": int(volume),
                    "relative_volume": round(relative_volume, 2)
                })
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
    # Sort by absolute % change descending
    results.sort(key=lambda x: abs(x["percent_change"]), reverse=True)
    return results
