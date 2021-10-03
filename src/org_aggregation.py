import math
import json
import pandas as pd
import numpy as np
from loguru import logger
from sparklines import sparklines


def quant_90(x):
    return x.quantile(.9)


def quant_10(x):
    return x.quantile(.1)


def hist(x):
    log_bins = np.histogram([math.log10(y+1) for y in x])[0]
    return "".join(sparklines(log_bins)) + f" {max(x):,.0f}"


def bins(x):
    lin_bins = np.histogram(x)[0]
    log_bins = np.histogram([math.log10(y+1) for y in x])[0]
    return ",".join(str(x) for x in lin_bins) + " :: " + ",".join(str(x) for x in log_bins)


def write_agg_data():
    in_filename = "github_data_FULL.pkl"
    output_csv_filename = "__github_data_agg.csv"
    output_json_filename = "__github_data_agg.json"

    # Read data
    df_raw = pd.read_pickle(in_filename)
    logger.info(f"pickle input shape: {df_raw.shape}")
    logger.info(f"pickle input cols: {', '.join([x for x in df_raw.columns.sort_values()])}")

    # df_raw = df_raw.drop(columns=["description", "featured", "links", "subcategory", "githuburl"])
    df_raw = df_raw.drop(columns=["description"])  # Unused google sheet description col
    df_raw["org"] = df_raw["_repopath"].apply(lambda x: x.split("/")[0].lower())
    df_raw.columns = [x.lstrip("_") for x in df_raw.columns]
    logger.info(f"pickle processed shape: {df_raw.shape}")
    logger.info(f"pickle processed cols: {', '.join([x for x in df_raw.columns.sort_values()])}")

    df = (df_raw
          .sort_values(by=["stars"], ascending=False)
          .groupby(["org"])
          .agg({
                "description": ["first"],
                "org": ["count"],
                "stars": ["mean", "median", "max", "min", hist],  #, quant_10, quant_90],
                "forks": ["mean", "median", "max", "min"],
                "watches": ["mean", "median", "max", "min"],
                "age_weeks": ["mean", "median", "max", "min", hist],
                "stars_per_week": ["mean", "median", "max", "min", hist],
                "created_at": ["max", "min"],
                "updated_at": ["max", "min"],
                "last_commit_date": ["max", "min"],
               })
          .round(2)
          )

    df.columns = ["_".join(x) for x in df.columns.to_flat_index()]
    df = df.rename(columns={"description_first": "desc_most_stars", "org_count": "repo_count"})
    sort_by = "stars_max"
    # sort_by = "repo_count"
    df = df.sort_values(by=[sort_by], ascending=False)
    df = df.reset_index()
    logger.info(f"agg shape: {df.shape}")

    # Write to files
    df.to_csv(output_csv_filename)

    with open(output_json_filename, "w") as f:
        json_results = df.to_json(orient="table", double_precision=2)
        data = json.loads(json_results)
        json.dump(data, f, indent=4)

    # display(HTML(df.to_html(index=False)))


# def write_min_json():
#     in_filename = "github_data.json"
#     out_filename = "github_data.min.json"
#
#     with open(in_filename, "r") as f:
#         d = json.load(f)
#
#     with open(out_filename, "w") as f:
#         json.dump(d, f, separators=(',', ':'))



