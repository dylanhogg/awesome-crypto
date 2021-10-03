import crawler
import org_aggregation
from library import log, env
from library.ghw import GithubWrapper


def main():
    log.configure()

    # NOTE: csv location can be local file or google spreadsheet, for example:
    #       https://docs.google.com/spreadsheets/d/<your_doc_id>/export?gid=0&format=csv
    csv_location = env.get("CSV_LOCATION")
    token = env.get("GITHUB_ACCESS_TOKEN")
    output_csv_filename = "github_data.csv"
    output_json_filename = "github_data.json"
    ghw = GithubWrapper(token)

    crawler.process(csv_location, ghw, output_csv_filename, output_json_filename)


if __name__ == "__main__":
    # main()
    org_aggregation.write_agg_data()
