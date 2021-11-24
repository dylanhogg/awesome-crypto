# Deployment

## New deployment

Run app to generate local md files, data folder and github_data.json/csv files

```
make run
```


Deploy Server API (S3, R53, Certificate, Cloudfront)

```
cd server
make tf-init
make tf-plan (check correct naming etc in variables.tfvars
make tf-apply
make s3-deploy-files
```

Deploy Client Website

```
cd client
make tf-init
make tf-plan (check correct naming etc in variables.tfvars
make tf-apply
make s3-deploy-app
```


Data Refresh

```
1) Update local API data and /data README files
TODO: WIP: Clear /_coingeko folder to skip cache of market data on Organisation page
make run

2) Run locally to view changes
cd client; make copy-data-local-app; make serve-local-app
Visit localhost:8004

3) Commit `/categories` and `/api_data` folders to github

4) Deploy server api data
cd server
make s3-deploy-files
make cf-invalidation

5) Deploy client app
Ensure client/app/app.js references full URL for ajax data, not local test URL
cd ../client
make s3-deploy-app
make cf-invalidation

6) Steps to only update market data
TODO: check this
Run app with include_crawl_github=False in main:
    `main(include_crawl_github=False, include_org_data_update=True)`

```