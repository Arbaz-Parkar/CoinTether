# src/price_fetcher.py

import requests

SYMBOL_TO_ID = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'DOGE': 'dogecoin',
    'SOL': 'solana',
    'ADA': 'cardano',
    'BNB': 'binancecoin',
    'XRP': 'ripple',
    'MATIC': 'matic-network',
    'LTC': 'litecoin',
    'DOT': 'polkadot',
    'SHIB': 'shiba-inu',
    'AVAX': 'avalanche-2',
    'TRX': 'tron',
    'UNI': 'uniswap',
    'XLM': 'stellar'
}

def fetch_prices(symbols):
    print("Fetching prices for:", symbols)

    ids = []
    symbol_map = {}

    for sym in symbols:
        sym_upper = sym.upper()
        if sym_upper in SYMBOL_TO_ID:
            coingecko_id = SYMBOL_TO_ID[sym_upper]
            ids.append(coingecko_id)
            symbol_map[coingecko_id] = sym_upper

    if not ids:
        print("No valid IDs found for symbols.")
        return {"error": "No valid coins matched with CoinGecko API. Check your symbols."}

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ','.join(ids),
        "order": "market_cap_desc",
        "per_page": len(ids),
        "page": 1,
        "sparkline": "false"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print("Request URL:", response.url)
        print("Status Code:", response.status_code)
        response.raise_for_status()

        data = response.json()
        print("API Response:\n", data)

        prices = {}
        for coin in data:
            sym = symbol_map.get(coin["id"])
            if sym:
                prices[sym] = {
                    "usd": coin.get("current_price", "N/A"),
                    "inr": coin.get("current_price", 0) * 83,  # crude INR conversion
                    "image": coin.get("image")
                }

        print("Final price dictionary:", prices)
        return prices

    except Exception as e:
        print("Exception occurred while fetching prices:", str(e))
        return {"error": str(e)}

