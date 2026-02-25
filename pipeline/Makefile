#!make

.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "[End]"

.PHONY: clean
clean: ## Remove build artifacts and generated template.
	@echo "Removing build artifacts..."
	@rm -rf ./.aws-sam/
	@find . -type d -name __pycache__ | xargs rm -rf {} \;
	@echo "[End]"

.PHONY: deploy-dev
deploy-dev: build-dev ## Deploys the built base cloudformation template
	@echo "Deploying the base cloudformation template."
	@sam deploy --config-env dev --disable-rollback
	@echo "[End]"

.PHONY: build-prod
build-prod: clean ## Builds the base cloudformation template
	@echo "Building the base cloudformation template."
	@sam build --config-env prod
	@echo "[End]"

.PHONY: deploy-prod
deploy-prod: build-prod ## Deploys the built base cloudformation template
	@echo "Deploying the base cloudformation template."
	@sam deploy --config-env prod
	@echo "[End]"

.PHONY: build-dev
build-dev: clean ## Builds the base cloudformation template
	@echo "Building the base cloudformation template."
	@sam build --config-env dev
	@echo "[End]"