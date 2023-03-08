import math
import json
import pandas as pd
import numpy as np
import market_data
from loguru import logger
from sparklines import sparklines


def quant_90(x):
    return x.quantile(0.9)


def quant_10(x):
    return x.quantile(0.1)


def first5(x):
    data = x[0:5]
    return ",".join(str(x) for x in data)


def hist(x):
    log_bins = np.histogram([math.log10(y + 1) for y in x])[0]
    return "".join(sparklines(log_bins)) + f"<br />{min(x):,.0f} to {max(x):,.0f}"


def bins(x):
    lin_bins = np.histogram(x)[0]
    log_bins = np.histogram([math.log10(y + 1) for y in x])[0]
    return (
        ",".join(str(x) for x in lin_bins) + " :: " + ",".join(str(x) for x in log_bins)
    )


def write_agg_data(
    in_repo_filename,
    in_ticker_filename,
    output_org_csv_filename,
    output_org_json_filename,
):
    # Read repo detail data
    df_raw = pd.read_pickle(in_repo_filename)
    logger.info(f"write_agg_data with input cols: {df_raw.columns}")
    logger.info(f"pickle input shape: {df_raw.shape}")
    logger.info(
        f"pickle input cols: {', '.join([x for x in df_raw.columns.sort_values()])}"
    )

    df_raw["org"] = df_raw["_repopath"].apply(lambda x: x.split("/")[0].lower())
    df_raw.columns = [x.lstrip("_") for x in df_raw.columns]
    logger.info(f"pickle processed shape: {df_raw.shape}")
    logger.info(
        f"pickle processed cols: {', '.join([x for x in df_raw.columns.sort_values()])}"
    )

    # DEBUG: Find last_commit_date errors causing groupby error(s):
    # df_raw["last_commit_date_correct"] = pd.to_datetime(
    #     df_raw["last_commit_date"], errors="coerce"
    # )
    # errors = df_raw.loc[df_raw["last_commit_date_correct"].isnull()][
    #     ["repopath", "last_commit_date"]
    # ]
    # logger.exception(f"last_commit_date value errors:\n{errors}")
    # df_raw["last_commit_date"] = pd.to_datetime(
    #     df_raw["last_commit_date"], errors="coerce"
    # )

    # Perform aggregation by org
    df = (
        df_raw.sort_values(by=["stars"], ascending=False)
        .groupby(["org"])
        .agg(
            {
                "repopath": [first5],
                "description": ["first"],
                "org": ["count"],
                "stars": ["mean", "median", "max", "min", "sum", hist],
                "forks": ["mean", "median", "max", "min", "sum"],
                "watches": ["mean", "median", "max", "min", "sum"],
                "age_weeks": ["mean", "median", "max", "min", hist],
                "stars_per_week": ["mean", "median", "max", "min", "sum", hist],
                "created_at": ["max", "min"],
                "updated_at": ["max", "min"],
                "last_commit_date": ["max", "min"],
            }
        )
        .round(2)
    )
    logger.info(f"Agg df:\n{df}")

    df.columns = ["_".join(x) for x in df.columns.to_flat_index()]
    df = df.rename(
        columns={"description_first": "desc_most_stars", "org_count": "repo_count"}
    )
    sort_by = "stars_max"
    df = df.sort_values(by=[sort_by], ascending=False)
    df = df.reset_index()
    logger.info(f"agg shape: {df.shape}")

    # Join/merge ticker data on github organisation name
    # NOTE: ticker_lookup.csv is externally generated with manual additions. Will include code eventually.
    # TODO: replace in_ticker_filename with just coingecko data
    df_ticker = pd.read_csv(in_ticker_filename)
    df_results = pd.merge(df, df_ticker, on="org", how="left").drop(
        columns=["ticker_count"]
    )

    # TODO: This market_cap addition is very hacky, fix me up
    df_results["market_cap_usd_mil"] = df_results["ticker"].apply(
        lambda x: ""
        if market_data.get_coins_by_symbol(x, "usd") is None
        else market_data.get_coins_by_symbol(x, "usd")["market_cap"] / 1e6
    )
    df_results["market_cap_rank"] = df_results["ticker"].apply(
        lambda x: ""
        if market_data.get_coins_by_symbol(x, "usd") is None
        else market_data.get_coins_by_symbol(x, "usd")["market_cap_rank"]
    )
    df_results["market_cap_datetime"] = df_results["ticker"].apply(
        lambda x: ""
        if market_data.get_coins_by_symbol(x, "usd") is None
        else market_data.get_coins_by_symbol(x, "usd")["market_cap_datetime"]
    )

    # Write to files
    df_results.to_csv(output_org_csv_filename)

    with open(output_org_json_filename, "w") as f:
        json_results = df_results.to_json(orient="table", double_precision=2)
        data = json.loads(json_results)
        json.dump(data, f, indent=4)
