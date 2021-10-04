import time
import github
from loguru import logger
from typing import List


class GithubWrapper:
    def __init__(self, token, throttle_secs):
        self.gh = github.Github(token)
        self.cache = {}
        self.throttle_secs = throttle_secs
        self.get_repo_cache_miss_count = 0
        self.get_repo_cache_hit_count = 0

    def get_repo(self, name, use_cache=True, throttled=True) -> github.Repository:
        if name.endswith("/"):
            logger.warning(f"Repo needs to be fixed by removing trailing slash in source csv: {name}")
        if name.endswith("*"):
            logger.warning(f"Repo needs to be fixed by exploding wildcard repo in source csv: {name}")
        if throttled:
            time.sleep(self.throttle_secs)

        key = f"repo_{name}"
        cached = self.cache.get(key, None)
        if cached is None or not use_cache:
            self.get_repo_cache_miss_count += 1
            logger.info(f"get_repo: [{name}] (cache miss {self.get_repo_cache_miss_count})")
            try:
                self.cache[key] = self.gh.get_repo(name)
            except Exception as ex:
                logger.warning(f"Exception for name (will re-try once): {name}")
                try:
                    time.sleep(15)
                    self.cache[key] = self.gh.get_repo(name)
                except Exception as ex:
                    logger.error(f"Exception for name: {name}")
                    raise ex
            return self.cache[key]
        else:
            self.get_repo_cache_hit_count += 1
            logger.info(f"get_repo: [{name}] (cache hit {self.get_repo_cache_hit_count})")
            return cached

    def get_org_repos(self, name, throttled=True) -> List[github.Repository.Repository]:
        logger.debug(f"get_org_repos: {name}")
        if throttled:
            time.sleep(self.throttle_secs)
        org = self.gh.get_organization(name)
        repos = []
        for repo in org.get_repos():
            repos.append(repo)
        return repos

    def get_organization(self, name, throttled=True) -> github.Organization.Organization:
        logger.debug(f"get_organization: {name}")
        if throttled:
            time.sleep(self.throttle_secs)
        return self.gh.get_organization(name)

    def search_github(self, keywords, throttled=True):
        logger.debug(f"search_github: {keywords}")
        if throttled:
            time.sleep(self.throttle_secs)

        query = "+".join(keywords) + "+in:readme+in:description"
        result = self.gh.search_repositories(query, "stars", "desc")
        print(f"Found {result.totalCount} repo(s)")
        for repo in result:
            print(repo.clone_url)
