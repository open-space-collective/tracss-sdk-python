.DEFAULT_GOAL := help


.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'


SPEC_PAIRS := \
	bulk_data::https://api.tracss.gov/bulkdata/api-docs \
	metadata::https://api.tracss.gov/metadata/api-docs/metadata \
	subscriber::https://api.tracss.gov/subscriber/api-docs

.PHONY: specs
specs: ## Fetch OpenAPI specs from TraCSS
	@echo "Fetching OpenAPI specs..."
	@for pair in $(SPEC_PAIRS); do \
	name=$$(echo $$pair | cut -d: -f1); \
	url=$$(echo $$pair | cut -d: -f3-); \
	echo "- fern/openapi/$$name/openapi.json ($$url)"; \
	mkdir -p fern/openapi/$$name; \
	curl -fsSL "$$url" -o fern/openapi/$$name/openapi.json; \
	done
	@python3 -c "import json,pathlib; f=pathlib.Path('fern/openapi/subscriber/openapi.json'); d=json.loads(f.read_text()); [p.update({'required':False}) for p in d['paths']['/subscriber/messages']['get']['parameters'] if p.get('name')=='fields' and p.get('in')=='query']; f.write_text(json.dumps(d,indent=2)); print('  - subscriber/openapi.json: fields param set optional')"
	@echo -n "Specs updated"
	@if ! git diff --quiet fern/openapi/; then \
	echo "."; \
	git diff --stat fern/openapi/; \
	else \
	echo " (no changes from previous fetch)."; \
	fi


.PHONY: check
check: ## Validate Fern config (no generation)
	fern check

.PHONY: generate
generate: ## Generate SDK (requires fern login)
	fern generate --group python-sdk --local


.PHONY: docs-dev
docs-dev: ## Start local docs preview server at localhost:3000
	fern docs dev

.PHONY: docs-preview
docs-preview: ## Generate shareable docs preview URL (requires FERN_TOKEN or fern login)
	fern generate --docs --preview


.PHONY: install
install: ## Install workspace dependencies
	uv sync

LINT_TARGETS := sdks/python/tracss/client.py tests/

.PHONY: lint
lint: ## Lint + format check (hand-written files only)
	uv run ruff check $(LINT_TARGETS)
	uv run ruff format --check $(LINT_TARGETS)

.PHONY: fmt
fmt: ## Auto-fix lint + formatting (hand-written files only)
	uv run ruff format $(LINT_TARGETS)
	uv run ruff check --fix $(LINT_TARGETS)

.PHONY: typecheck
typecheck: ## Run mypy on hand-written files
	uv run mypy sdks/python/tracss/client.py tests/

.PHONY: test
test: ## Run unit tests with coverage
	uv run pytest tests/unit/ -v


SUBSCRIBER_PORT ?= 4010
BULKDATA_PORT   ?= 4011
METADATA_PORT   ?= 4012

.PHONY: prism-subscriber
prism-subscriber: ## Start Prism mock server for subscriber (port 4010)
	npx --yes @stoplight/prism-cli mock fern/openapi/subscriber/openapi.json --port $(SUBSCRIBER_PORT)

.PHONY: prism-bulkdata
prism-bulkdata: ## Start Prism mock server for bulkdata (port 4011)
	npx --yes @stoplight/prism-cli mock fern/openapi/bulk_data/openapi.json --port $(BULKDATA_PORT)

.PHONY: prism-metadata
prism-metadata: ## Start Prism mock server for metadata (port 4012)
	npx --yes @stoplight/prism-cli mock fern/openapi/metadata/openapi.json --port $(METADATA_PORT)

.PHONY: prism-all
prism-all: ## Start all three Prism mock servers in the background and wait for readiness
	@for spec_port in \
		"fern/openapi/subscriber/openapi.json:::$(SUBSCRIBER_PORT)" \
		"fern/openapi/bulk_data/openapi.json:::$(BULKDATA_PORT)" \
		"fern/openapi/metadata/openapi.json:::$(METADATA_PORT)"; do \
		spec=$$(echo $$spec_port | cut -d: -f1); \
		port=$$(echo $$spec_port | cut -d: -f4-); \
		if ! curl -s --max-time 0.5 http://localhost:$$port > /dev/null 2>&1; then \
			npx --yes @stoplight/prism-cli mock "$$spec" --port $$port & \
		fi; \
	done
	@for port in $(SUBSCRIBER_PORT) $(BULKDATA_PORT) $(METADATA_PORT); do \
		timeout 15 bash -c \
			"until curl -s --max-time 2 http://localhost:$$port > /dev/null 2>&1; do sleep 0.5; done" \
			|| { echo "Prism did not start on port $$port" >&2; exit 1; }; \
	done

.PHONY: prism-stop
prism-stop: ## Stop all Prism mock servers
	-pkill -f "prism mock" 2>/dev/null || true

.PHONY: integration
integration: ## Run integration tests (requires prism-all running)
	TRACSS_SUBSCRIBER_URL=http://localhost:$(SUBSCRIBER_PORT) \
	TRACSS_BULKDATA_URL=http://localhost:$(BULKDATA_PORT) \
	TRACSS_METADATA_URL=http://localhost:$(METADATA_PORT) \
	TRACSS_CLIENT_ID=fake \
	TRACSS_CLIENT_SECRET=fake \
	uv run pytest tests/integration/ -v -m integration


.PHONY: build
build: ## Build distribution wheel and validate with twine
	uv build --package tracss
	uv run twine check dist/*

.PHONY: publish
publish: build ## Publish to PyPI (requires PYPI_TOKEN env var)
	uv publish --token $$PYPI_TOKEN

.PHONY: clean
clean: ## Remove build artifacts and caches
	rm -rf dist/ .pytest_cache/ .mypy_cache/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.egg-info" -exec rm -rf {} +


.PHONY: smoke
smoke: ## Run smoke tests against the live TraCSS API (requires real credentials in env)
	uv run pytest tests/smoke/ -v -m smoke

.PHONY: security
security: ## Run security scans (bandit static analysis + pip-audit vulnerability check)
	uv run bandit -r sdks/python/tracss/client.py tests/ -ll
	uv run pip-audit

.PHONY: coverage
coverage: ## Generate HTML coverage report (open htmlcov/index.html)
	uv run pytest tests/unit/ --cov=tracss.client --cov-report=html
