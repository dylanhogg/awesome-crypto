import json
from datetime import datetime
from loguru import logger
from library import render, readme, input


def process(csv_location, ghw, output_csv_filename, output_json_filename, throttle_secs):
    start = datetime.now()

    # Read github urls from google docs
    df_input = input.get_input_data(csv_location, ghw)
    # df_input = df_input.head(2)  # Testing

    # Augment repo name with metadata from Github
    logger.info(f"Processing {len(df_input)} records from {csv_location}")
    df = render.process(df_input, ghw, throttle_secs)

    # Write raw results to csv
    logger.info(f"Write raw results to csv...")
    df.to_csv(output_csv_filename)

    logger.info("Crawling readme files...")
    df["_readme_filename"] = df["_repopath"].apply(
        lambda x: readme.get_readme(x)
    )

    # TODO: handle 'main' master branches also:
    df["_readme_giturl"] = df.apply(
        lambda row: f"https://raw.githubusercontent.com/{row['_repopath']}/master/{row['_readme_filename']}"
                    if len(row['_readme_filename']) > 0
                    else "", axis=1
    )

    # TODO: get from readme.get_readme above as tuple and zip as per
    #       https://stackoverflow.com/questions/16236684/apply-pandas-function-to-column-to-create-multiple-new-columns
    df["_readme_localurl"] = df.apply(
        lambda row: f"{row['_repopath'].replace('/', '~')}~{row['_readme_filename']}"
                    if len(row['_readme_filename']) > 0
                    else "", axis=1
    )

    # TODO: review:
    # Drop unused UI columns before writing to files
    df = df.drop(columns=["description", "featured", "links", "subcategory"])

    # Write raw results to json
    with open(output_json_filename, "w") as f:
        json_results = df.to_json(orient="table", double_precision=2)
        data = json.loads(json_results)
        json.dump(data, f, indent=4)

    # Write raw results to minimised json
    output_minjson_filename = output_json_filename.replace(".json", ".min.json") \
        if ".json" in output_json_filename \
        else output_json_filename + ".min.json"

    with open(output_minjson_filename, "w") as f:
        json_results = df.to_json(orient="table", double_precision=2)
        data = json.loads(json_results)
        json.dump(data, f, separators=(',', ':'))

    # Write raw results to pickle
    output_pickle_filename = output_json_filename.replace(".json", ".pkl") \
        if ".json" in output_json_filename \
        else output_json_filename + ".pkl"
    df.to_pickle(output_pickle_filename)

    # Add markdown columns for local README.md and categories/*.md file lists.
    logger.info(f"Add markdown columns...")
    df = render.add_markdown(df)

    # Write all results to README.md
    lines_footer = [
        f"This file was automatically generated on {datetime.now().date()}.  "
        f"\n\nTo curate your own github list, simply clone and change the input csv file.  "
    ]
    lines = []
    lines.extend(render.lines_header(len(df)))
    lines.extend(list(df["_doclines_main"]))
    lines.extend(lines_footer)

    logger.info(f"Writing {len(df)} entries to README.md...")
    with open("README.md", "w") as out:
        out.write("\n".join(lines))

    # Write to organisations
    organisations = df["_organization"].unique()
    for org in organisations:
        df_org = df[df["_organization"] == org]
        lines = []
        lines.extend(render.lines_header(len(df_org), org))
        lines.extend(list(df_org["_doclines_child"]))
        lines.extend(lines_footer)
        filename = f"categories/{org.lower()}.md"
        logger.info(f"Writing {len(df_org)} entries to {filename}...")
        with open(filename, "w") as out:
            out.write("\n".join(lines))

    logger.info(f"Finished writing in {datetime.now() - start}")
