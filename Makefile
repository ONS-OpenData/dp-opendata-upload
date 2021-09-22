
# Build, tag, push and deploy/update a lamda via an updated image
.PHONY: build
build:
	@# Confirm we've been given the name of a lambda via a kwarg
	@if [ -z "$(lambda)" ]; then \
		echo "No lambda name provided."; \
		exit 1; \
	fi
	@# Confirm we have an env var with the ecr url in it
	@if [[ -z "${AWS_ECR_URL}" ]]; then \
		echo "You need to set the envionment variable AWS_ECR_URL."; \
		exit 1; \
	fi
	docker build --build-arg LAMBDA_NAME=$(lambda) -t $(lambda) . --no-cache
	docker tag  $(lambda):latest ${AWS_ECR_URL}/$(lambda):latest
	docker push ${AWS_ECR_URL}/$(lambda):latest
	aws lambda update-function-code --function-name $(lambda) --image-uri ${AWS_ECR_URL}/$(lambda):latest

# Register a lambda name with the aws ecr
.PHONY: register
register:
	@# Confirm we've been given the name of a lambda via a kwarg
	@if [ -z "$(lambda)" ]; then \
		echo "No lambda name provided."; \
		exit 1; \
	fi
	aws ecr create-repository --repository-name $(lambda) --image-scanning-configuration scanOnPush=false --image-tag-mutability MUTABLE

# Aurthenticate docker client
.PHONY: auth
auth:
	@# Confirm we have an env var with the ecr url in it
	@if [[ -z "${AWS_ECR_URL}" ]]; then \
		echo "You need to set the envionment variable AWS_ECR_URL."; \
		exit 1; \
	fi
	@# Confirm we've been given the name of a lambda via a kwarg
	@if [ -z "$(region)" ]; then \
		echo "No aws region provided."; \
		exit 1; \
	fi
	aws ecr get-login-password --region $(region) | docker login --username AWS --password-stdin $(AWS_ECR_URL)