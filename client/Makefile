.EXPORT_ALL_VARIABLES:
APP_NAME=crazy-awesome-crypto
ENV=prd
AWS_PROFILE=prd-non-tf-905234897161
AWS_ACCOUNT_ID=905234897161
AWS_REGION=us-east-1
BUCKET_NAME=awesome-crypto.infocruncher.com

# Local running

## Serve local js client app
serve-local-app:
	# cd app; python3 -m http.server 8004
	python3 http_server.py

## Copy processed data to local client for testing
copy-data-local-app: remove-data-local-app
	cp ../api_data/github_data.json app/
	cp ../api_data/github_data.min.json app/
	cp ../api_data/github_data.ui.min.json app/
	cp ../api_data/github_data_org.json app/
	cp -r ../data app/data

## Remove processed data from local client for testing
remove-data-local-app:
	rm app/github_data.json || true
	rm app/github_data.min.json || true
	rm app/github_data.ui.min.json || true
	rm app/github_data_org.json || true
	rm -rf app/data

## Browse local js client
browse-s3-app:
	open http://${BUCKET_NAME}/

## Browse to public S3 url
browse-s3:
	open http://${BUCKET_NAME}.s3-website-${AWS_REGION}.amazonaws.com/


# AWS Command Tools

## AWS S3 cp app to S3
s3-deploy-app-full: remove-data-local-app
	aws s3 cp app s3://${BUCKET_NAME} --recursive --profile ${AWS_PROFILE}
	aws s3 cp ../api_data/github_data.json s3://${BUCKET_NAME}/github_data.json --profile ${AWS_PROFILE}
	aws s3 cp ../api_data/github_data.min.json s3://${BUCKET_NAME}/github_data.min.json --profile ${AWS_PROFILE}
	aws s3 cp ../api_data/github_data.ui.min.json s3://${BUCKET_NAME}/github_data.ui.min.json --profile ${AWS_PROFILE}
	aws s3 cp ../api_data/github_data_org.json s3://${BUCKET_NAME}/github_data_org.json --profile ${AWS_PROFILE}
	aws s3 cp ../api_data/github_data.csv s3://${BUCKET_NAME}/github_data.csv --profile ${AWS_PROFILE}
	# aws s3 cp ../data s3://${BUCKET_NAME}/data --recursive --profile ${AWS_PROFILE}
	# NOTE: Remember to invalidate Cloudfront cache to materialise changes: "make cf-invalidation"

## AWS S3 cp app to S3 (no data)
s3-deploy-app-only: remove-data-local-app
	aws s3 cp app s3://${BUCKET_NAME} --recursive --profile ${AWS_PROFILE}
	# NOTE: Remember to invalidate Cloudfront cache to materialise changes: "make cf-invalidation"

## AWS S3 cp sitemap.xml to S3
s3-deploy-app-sitemap:
	aws s3 cp app/sitemap.xml s3://${BUCKET_NAME}/sitemap.xml --profile ${AWS_PROFILE}
	# NOTE: Remember to invalidate Cloudfront cache to materialise changes: "make cf-invalidation"

## AWS S3 rm static_files from S3
s3-delete-app:
	echo "Are you sure?"
	# aws s3 rm s3://${BUCKET_NAME} --recursive

## AWS Cloudfront invalidation (limit 1000 free calls per month)
cf-invalidation:
	# awesome-crypto.infocruncher.com:
	AWS_PAGER="" aws cloudfront create-invalidation --distribution-id E1TZP5ELNUI17P --paths "/*"
	# www.awesomecrypto.xyz:
	AWS_PAGER="" aws cloudfront create-invalidation --distribution-id E1U4N1DFRC0OPT --paths "/*"
	# awesomecrypto.xyz:
	AWS_PAGER="" aws cloudfront create-invalidation --distribution-id ECZV508344GZA --paths "/*"

# Terraform

## TF init
tf-init:
	cd infra; terraform init -var-file=variables.tfvars; cd -

## TF validate
tf-validate:
	cd infra; terraform validate; cd -

## TF plan
tf-plan:
	cd infra; terraform plan -var-file=variables.tfvars; cd -

## TF apply
tf-apply: tf-plan
	cd infra; terraform apply -var-file=variables.tfvars -auto-approve; cd -

## TF destroy
tf-destroy:
	cd infra; terraform destroy -var-file=variables.tfvars -auto-approve; cd -


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
