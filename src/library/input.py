import sys
import time
import pandas as pd
from joblib import Memory
from loguru import logger
from urllib.parse import urlparse

memory = Memory(".joblib_cache")


def get_input_data(csv_location, ghw) -> pd.DataFrame:
    df = pd.read_csv(csv_location)
    df.columns = map(str.lower, df.columns)
    assert "githuburl" in df.columns
    assert "category" in df.columns

    duplicated_githuburls = df[df.duplicated(subset=["githuburl"])]
    duplicated_count = len(duplicated_githuburls)
    if duplicated_count > 0:
        logger.warning(
            f"Duplicate githuburl values found in csv: {duplicated_count}\n{duplicated_githuburls}"
        )
        logger.error(
            f"Fix up {duplicated_count} duplicates from {csv_location} and re-run."
        )
        sys.exit()
    else:
        logger.info("No duplicate githuburl values found in csv :)")

    # If testing, limit input repos for expanding
    # logger.warning("Testing mode 2 on")
    # return df.drop(df[df.githuburl.str.endswith("/*")].index)[0:2]  # Testing

    df_normal_repos, df_expanded_repos = _explode_org_repos(df, ghw)
    df_concat = pd.concat([df_normal_repos, df_expanded_repos])
    print(f"Total concat wildcard and normal repos: {len(df_concat.index)}")

    # TEMP - maybe use as an optional cache?
    df_normal_repos.to_pickle("_df_normal_repos.pkl")
    df_expanded_repos.to_pickle("_df_expanded_repos.pkl")

    return df_concat


@memory.cache
def _cached_get_org_repos(ghw, org):
    return ghw.get_org_repos(org)


def _explode_org_repos(df, ghw):
    wildcard_row_mask = df.githuburl.str.endswith("/*")
    df_normal_repos = df.drop(df[wildcard_row_mask].index)

    df_wildcard_repos = df[wildcard_row_mask]
    wildcard_repos_list = list(df_wildcard_repos.itertuples(index=False))

    star_limit = 10  # TODO: append to spreadsheet record? or dynamically calculate?
    exploded_rows = []
    logger.info(f"Expaning wildcard repos (star_limit = {star_limit})...")
    for row in wildcard_repos_list:
        org = urlparse(row.githuburl).path.lstrip("/").rstrip("/*")
        logger.info(f"Read repos for wildcard org: {org}...")
        time.sleep(1)
        # org_repos = ghw.get_org_repos(org)
        org_repos = _cached_get_org_repos(ghw, org)
        giturls = [
            [
                row.category,
                row.subcategory,
                "https://github.com/" + org_repo.full_name,
                row.featured,
                row.links,
                row.description,
            ]
            for org_repo in org_repos
            if org_repo.stargazers_count >= star_limit
        ]
        logger.info(
            f"Read repos for wildcard org: {org} ({len(giturls)} of {len(org_repos)} kept)"
        )
        exploded_rows.extend(giturls)

    df_expanded_repos = pd.DataFrame(exploded_rows, columns=df_normal_repos.columns)
    logger.info(f"Total matching wildcard repos: {len(exploded_rows)}")

    return df_normal_repos, df_expanded_repos
