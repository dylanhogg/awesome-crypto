import time
import pandas as pd
from datetime import datetime
from typing import List
from urllib.parse import urlparse
from loguru import logger


def make_markdown(row, include_category=False) -> str:
    url = row["githuburl"]
    name = row["_reponame"]
    organization = row["_organization"]
    homepage = row["_homepage"]
    homepage_display = (
        f"[{homepage}]({homepage})  \n[{url}]({url})"
        if homepage is not None and len(homepage) > 0
        else f"[{url}]({url})"
    )
    category = row["_organization"].lower().strip()  # categories are the git org, not the supplied category.
    category_display = (
        f"[{category}](categories/{category}.md) category, "
        if include_category and category is not None and len(category) > 0
        else ""
    )
    stars = row["_stars"]
    stars_per_week = row["_stars_per_week"]
    stars_per_week = round(stars_per_week, 2) if stars_per_week < 10 else int(stars_per_week)
    age_weeks = row["_age_weeks"]
    forks = row["_forks"]
    watches = row["_watches"]
    updated = row["_updated_at"]
    last_commit_date = row["_last_commit_date"]
    created = row["_created_at"]
    topics = row["_topics"]
    topics_display = (
        "\n<sub><sup>" + ", ".join(sorted(topics)) + "</sup></sub>"
        if len(topics) > 0
        else ""
    )
    description = row["_description"]
    language = row["_language"]

    header = f"[{name}]({url})" \
        if name == organization \
        else f"[{name}]({url}) by [{organization}](https://github.com/{organization})"

    return (
        f"### {header}  "
        f"\n{description}  "
        f"\n{homepage_display}  "
        f"\n{stars_per_week} stars per week over {age_weeks} weeks  "
        f"\n{stars:,} stars, {forks:,} forks, {watches:,} watches  "
        f"\n{category_display}created {created}, last commit {last_commit_date}, main language {language}  "
        f"{topics_display}"
        f"\n\n"
    )


def get_repo_topics(repo_obj, throttle_secs, throttled=True):
    if throttled:
        time.sleep(throttle_secs)
    logger.info(f"get_last_commit_date")
    return repo_obj.get_topics()


def get_last_commit_date(repo_obj, throttle_secs, throttled=True):
    if throttled:
        time.sleep(throttle_secs)
    logger.info(f"get_last_commit_date")
    # TODO: store 1st page of commits
    return repo_obj.get_commits().get_page(0)[0].last_modified


def process(df_input, ghw, throttle_secs) -> pd.DataFrame:
    df = df_input.copy()

    # TODO: more https://pygithub.readthedocs.io/en/latest/examples/Repository.html

    df["_repopath"] = df["githuburl"].apply(lambda x: urlparse(x).path.lstrip("/"))
    df["_repo_obj"] = df["_repopath"].apply(lambda x: ghw.get_repo(x))

    df["_reponame"] = df["_repo_obj"].apply(lambda x: x.name)
    df["_stars"] = df["_repo_obj"].apply(lambda x: x.stargazers_count)
    df["_forks"] = df["_repo_obj"].apply(lambda x: x.forks_count)
    df["_watches"] = df["_repo_obj"].apply(lambda x: x.subscribers_count)
    df["_topics"] = df["_repo_obj"].apply(lambda x: get_repo_topics(x, throttle_secs))
    df["_language"] = df["_repo_obj"].apply(lambda x: x.language)
    df["_homepage"] = df["_repo_obj"].apply(lambda x: x.homepage)

    df["_description"] = df["_repo_obj"].apply(
        lambda x: "" if x.description is None else x.description
    )
    df["_organization"] = df["_repopath"].apply(
        lambda x: x.split("/")[0]
    )
    df["_updated_at"] = df["_repo_obj"].apply(
        lambda x: x.updated_at.date()
    )
    df["_last_commit_date"] = df["_repo_obj"].apply(
        # E.g. Sat, 18 Jul 2020 17:14:09 GMT
        lambda x: datetime.strptime(
            get_last_commit_date(x, throttle_secs),
            "%a, %d %b %Y %H:%M:%S %Z",
        ).date()
    )
    df["_created_at"] = df["_repo_obj"].apply(
        lambda x: x.created_at.date()
    )
    df["_age_weeks"] = df["_repo_obj"].apply(
        lambda x: (datetime.now().date() - x.created_at.date()).days // 7
    )
    df["_stars_per_week"] = df["_repo_obj"].apply(
        lambda x: x.stargazers_count * 7 / (datetime.now().date() - x.created_at.date()).days
    )

    df = df.drop(columns=["_repo_obj"])

    return df.sort_values("_stars", ascending=False)


def lines_header(count, category="") -> List[str]:
    category_line = f"A list of {count} crypto project repos ordered by stars.  \n"
    if len(category) > 0:
        category_line = f"A list of {count} [{category}](https://github.com/{category}) project repos ordered by stars.  \n"

    return [
        f"# Crazy Awesome Crypto",
        category_line,
        f"Checkout the interactive version that you can filter and sort: ",
        f"[https://awesome-crypto.infocruncher.com/](https://awesome-crypto.infocruncher.com/)  \n\n",
    ]


def add_markdown(df) -> pd.DataFrame:
    df["_doclines_main"] = df.apply(
        lambda x: make_markdown(x, include_category=True), axis=1
    )
    df["_doclines_child"] = df.apply(
        lambda x: make_markdown(x, include_category=False), axis=1
    )
    return df
