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
