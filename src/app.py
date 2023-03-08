import github_data
import org_aggregation
from loguru import logger
from library import log, env
from library.ghw import GithubWrapper


def main(include_crawl_github, include_org_data_update):
    log.configure()

    # NOTE: csv location can be local file or google spreadsheet, for example:
    #       https://docs.google.com/spreadsheets/d/<your_doc_id>/export?gid=0&format=csv
    csv_location = env.get("CSV_LOCATION")
    token = env.get("GITHUB_ACCESS_TOKEN")
    output_csv_filename = "api_data/github_data.csv"
    output_json_filename = "api_data/github_data.json"
    throttle_secs = float(env.get("THROTTLE_SECS"))

    logger.info(f"csv_location = {csv_location}")
    logger.info(f"output_csv_filename = {output_csv_filename}")
    logger.info(f"output_json_filename = {output_json_filename}")
    logger.info(f"throttle_secs = {throttle_secs}")

    ghw = GithubWrapper(token, throttle_secs)

    if include_crawl_github:
        # Crawl and write GitHub readme.md files & repo level API data csv/json
        github_data.process(
            csv_location, ghw, output_csv_filename, output_json_filename, throttle_secs
        )

    if include_org_data_update:
        # Aggregate repo level data by organisation
        in_repo_filename = "api_data/github_data.pkl"
        in_ticker_filename = "api_data/ticker_lookup.csv"
        output_org_csv_filename = "api_data/github_data_org.csv"
        output_org_json_filename = "api_data/github_data_org.json"
        org_aggregation.write_agg_data(
            in_repo_filename,
            in_ticker_filename,
            output_org_csv_filename,
            output_org_json_filename,
        )


# def temp_write_ui_min_json():
#     import json
#     import pandas as pd
#     output_json_filename = "api_data/github_data.json"
#     df = pd.read_json(output_json_filename, orient="table")
#
#     # Write UI results to minimised json (i.e. github_data.ui.min.json)
#     output_ui_minjson_filename = (
#         output_json_filename.replace(".json", ".ui.min.json")
#         if ".json" in output_json_filename
#         else output_json_filename + ".ui.min.json"
#     )
#     with open(output_ui_minjson_filename, "w") as f:
#         # NOTE: this cols list must be synced with app.js DataTable columns for display
#         cols = [
#             "githuburl",
#             "_reponame",
#             "_repopath",
#             "_description",
#             "_organization",
#             "_homepage",
#             "_stars",
#             "_stars_per_week",
#             "_forks",
#             "_updated_at",
#             "_created_at",
#             "_language",
#             "_topics",
#             "_readme_localurl",
#         ]
#         json_results = df[cols].to_json(orient="table", double_precision=2, index=False)
#         data = json.loads(json_results)
#         json.dump(data, f, separators=(",", ":"))


if __name__ == "__main__":
    main(include_crawl_github=True, include_org_data_update=True)
    # main(include_crawl_github=False, include_org_data_update=True)
    # temp_write_ui_min_json()
