import github_data
import org_aggregation
import market_data
from library import log, env
from library.ghw import GithubWrapper


def main():
    log.configure()

    # NOTE: csv location can be local file or google spreadsheet, for example:
    #       https://docs.google.com/spreadsheets/d/<your_doc_id>/export?gid=0&format=csv
    csv_location = env.get("CSV_LOCATION")
    token = env.get("GITHUB_ACCESS_TOKEN")
    output_csv_filename = "api_data/github_data.csv"
    output_json_filename = "api_data/github_data.json"
    throttle_secs = float(env.get("THROTTLE_SECS"))
    ghw = GithubWrapper(token, throttle_secs)

    # Crawl and write Github readme.md files & repo level API data csv/json
    github_data.process(csv_location, ghw, output_csv_filename, output_json_filename, throttle_secs)

    # Aggregate repo level data by organisation
    in_repo_filename = "api_data/github_data.pkl"
    in_ticker_filename = "api_data/ticker_lookup.csv"
    output_org_csv_filename = "api_data/github_data_org.csv"
    output_org_json_filename = "api_data/github_data_org.json"
    org_aggregation.write_agg_data(in_repo_filename, in_ticker_filename, output_org_csv_filename, output_org_json_filename)


if __name__ == "__main__":
    main()
