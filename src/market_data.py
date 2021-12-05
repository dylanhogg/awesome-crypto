import os
import json
import time
import datetime
import os.path
from pathlib import Path
from loguru import logger
from pycoingecko import CoinGeckoAPI

# NOTE: this is a WIP


def _get_coins_list(use_cache=True, filename="_coingecko/coins_list.json"):
    cg = CoinGeckoAPI()

    if use_cache and os.path.isfile(filename):
        logger.info(f"Loading from cache: {filename}")
        with open(filename) as f:
            return json.load(f)

    crawl_date = str(datetime.datetime.now())
    coins = cg.get_coins_list()
    for coin in coins:
        coin["_crawl_datetime"] = crawl_date

    folder = os.path.dirname(filename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    coin_json = json.dumps(coins, indent=4)
    with open(filename, "w") as f:
        f.write(coin_json)

    return coins


def _save_coin_by_id(coin_id, filename=None, skip_if_exists=True, throttle=3):
    cg = CoinGeckoAPI()
    if filename is None:
        filename = f"_coingecko/id_{coin_id}.json"

    if skip_if_exists and os.path.isfile(filename):
        logger.info(f"Skipping crawl of {coin_id}...")
        return

    logger.info(f"Crawling {coin_id}...")
    if throttle is not None:
        time.sleep(throttle)

    coin = cg.get_coin_by_id(coin_id)
    coin["_crawl_datetime"] = str(datetime.datetime.now())
    coin_json = json.dumps(coin, indent=4)
    with open(f"_coingecko/id_{coin_id}.json", "w") as f:
        f.write(coin_json)


def crawl_coins_by_cg_ids(coin_ids):
    for idx, coin_id in enumerate(coin_ids):
        _save_coin_by_id(coin_id)


def get_marketcap_by_cg_id(cg_id, currency="usd"):
    cg_api_filepath = "_coingecko"

    # TODO: handle crawl from api if file is too old?
    filename = f"{cg_api_filepath}/id_{cg_id}.json"
    if not os.path.isfile(filename):
        _save_coin_by_id(cg_id, filename)

    with open(filename) as f:
        data = json.load(f)
        market_cap = data["market_data"]["market_cap"][currency]
        market_cap_rank = data["market_cap_rank"]
        crawl_datetime = data["_crawl_datetime"]
        return market_cap, market_cap_rank, crawl_datetime


def get_coins_by_symbol(symbol, currency="usd"):
    if not isinstance(symbol, str):
        return None

    coins = []
    for coin in _get_coins_list():
        if coin["symbol"].lower() == symbol.lower():
            coin_id = coin["id"]
            market_cap, market_cap_rank, crawl_datetime = get_marketcap_by_cg_id(coin_id, currency)
            if market_cap > 0:
                coin["market_cap"] = market_cap
                coin["market_cap_rank"] = market_cap_rank
                coin["market_cap_datetime"] = crawl_datetime
                coins.append(coin)

    if len(coins) == 0:
        logger.error(f"get_coins_by_symbol couldn't get coin by symbol '{symbol}'")
        return None

    best_coin = coins[0]
    for coin in coins:
        if coin["market_cap_rank"] < best_coin["market_cap_rank"]:
            best_coin = coin

    return best_coin


def get_coins_by_symbols(symbols, currency="usd"):
    results = []
    for symbol in symbols:
        best_coin, coins = get_coins_by_symbol(symbol, currency)
        results.append(best_coin)
    return results


# Methods testing coingeko api:

def get_global(use_cache=True, filename="_coingecko/global.json"):
    # https://api.coingecko.com/api/v3/global
    cg = CoinGeckoAPI()

    if use_cache and os.path.isfile(filename):
        logger.info(f"Loading from cache: {filename}")
        with open(filename) as f:
            return json.load(f)

    crawl_date = str(datetime.datetime.now())
    response = cg.get_global()
    response["_crawl_datetime"] = crawl_date

    response_json = json.dumps(response, indent=4)
    with open(filename, "w") as f:
        f.write(response_json)

    return response


def get_prices(ids, use_cache=False, filename="_coingecko/_prices.json"):
    # https://api.coingecko.com/api/v3/simple/price?ids=ethereum%2Cbitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true
    cg = CoinGeckoAPI()

    if use_cache and os.path.isfile(filename):
        logger.info(f"Loading from cache: {filename}")
        with open(filename) as f:
            return json.load(f)

    crawl_date = str(datetime.datetime.now())
    prices = cg.get_price(ids,
                          vs_currencies='usd', include_market_cap='true', include_24hr_vol='true',
                          include_24hr_change='true', include_last_updated_at='true')

    if len(prices) != len(ids):
        logger.warning(f"get_prices only matched {len(prices)} of {len(ids)} requested ids")
    else:
        logger.info(f"get_prices matched all {len(prices)} of {len(ids)} requested ids")

    for coin in prices:
        prices[coin]["_crawl_datetime"] = crawl_date

    price_json = json.dumps(prices, indent=4)
    with open(filename, "w") as f:
        f.write(price_json)

    return prices

