import sys
import pandas as pd
from loguru import logger
from urllib.parse import urlparse


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
        logger.error(f"Fix up {duplicated_count} duplicates from {csv_location} and re-run.")
        sys.exit()
    else:
        logger.info("No duplicate githuburl values found in csv :)")

    df = explode_org_repos(df, ghw)
    return df


def explode_org_repos(df, ghw):

    wildcard_row_mask = df.githuburl.str.endswith("/*")
    df_wildcard_repos = df[wildcard_row_mask]
    wildcards = list(df_wildcard_repos["githuburl"])
    orgs = list(map(lambda x: urlparse(x).path.lstrip("/").rstrip("/*"), wildcards))
    orgs = orgs[0:1]  # Testing

    star_limit = 100  # TODO: append to spreadsheet record? or dynamically calculate?
    exploded_repos = []
    for org in orgs:
        logger.info(f"Getting repos for wildcard org: {org}")
        org_repos = ghw.get_org_repos(org)
        org_repo_names = [x.full_name for x in org_repos if x.stargazers_count >= star_limit]
        exploded_repos.extend(org_repo_names)

    exploded_repos = sorted(exploded_repos)
    print(exploded_repos)
    with open("_exploded_repos.txt", "w") as outfile:
        outfile.write("\n".join(exploded_repos))

    df_normal_repos = df.drop(df[wildcard_row_mask].index)

    # TOOD: insert exploded_repos

    return df_normal_repos
