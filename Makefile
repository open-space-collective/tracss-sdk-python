.DEFAULT_GOAL := help


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
.PHONY: help


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
	curl -fsSL --connect-timeout 10 --max-time 30 "$$url" -o fern/openapi/$$name/openapi.json; \
	done
	# Patch subscriber/openapi.json to make the 'fields' query param optional
	@python3 -c "\
import json,pathlib; \
f=pathlib.Path('fern/openapi/subscriber/openapi.json'); \
d=json.loads(f.read_text()); \
params=d['paths']['/subscriber/messages']['get']['parameters']; \
patched=[p for p in params if p.get('name')=='fields' and p.get('in')=='query']; \
assert len(patched)==1, f'Expected exactly 1 fields query param to patch; found {len(patched)}'; \
[p.update({'required':False}) for p in patched]; \
f.write_text(json.dumps(d,indent=2)); \
print('  - subscriber/openapi.json: fields param set optional')"
	# Prettify bulk_data/openapi.json and metadata/openapi.json
	@python3 -c "\
import json,pathlib; \
[pathlib.Path(p).write_text(json.dumps(json.loads(pathlib.Path(p).read_text()),indent=2)) \
 for p in ['fern/openapi/bulk_data/openapi.json','fern/openapi/metadata/openapi.json']]"
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
generate: ## Generate SDK (requires fern login or FERN_TOKEN)
	fern generate --group python-sdk --local
	$(MAKE) post-generate

.PHONY: post-generate
post-generate: ## Fix generated artifacts
	@# fern-python-sdk bug: uses Fern org name (open-space-collective) as Python module
	@# name in test_aiohttp_autodetect.py instead of the configured package_name.
	@# Patch before ruff runs so it doesn't trip on the invalid identifier.
	@if [ -f sdks/python/tracss/tests/test_aiohttp_autodetect.py ]; then \
	    sed -i 's/open-space-collective/tracss/g' \
	        sdks/python/tracss/tests/test_aiohttp_autodetect.py; \
	fi
	@# Fern generates docstring examples using `token="YOUR_TOKEN"` which is the
	@# generated BaseTraCSS interface, not the public TraCSS constructor that takes
	@# client_id/client_secret.  Patch every generated */client.py docstring.
	@find sdks/python/tracss -name 'client.py' ! -path '*/tracss/client.py' \
	    -exec sed -i 's/token="YOUR_TOKEN"/client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET"/g' {} +
	@# Wire __version__ into the lazy-loader so `tracss.__version__` works at runtime.
	@# _version.py is protected by .fernignore; __init__.py is regenerated each run.
	@sed -i 's/"subscriber": ".subscriber"}/"subscriber": ".subscriber", "__version__": "._version"}/' \
	    sdks/python/tracss/__init__.py
	@# Expose hand-written RawResponse (from client.py) via the top-level package.
	@# Three patches: _dynamic_imports dict, __all__ list, TYPE_CHECKING import.
	@sed -i 's/"TraCSS": ".client"/"RawResponse": ".client", "TraCSS": ".client"/' \
	    sdks/python/tracss/__init__.py
	@sed -i 's/"TraCSS", "TraCSSEnvironment"/"RawResponse", "TraCSS", "TraCSSEnvironment"/' \
	    sdks/python/tracss/__init__.py
	@sed -i 's/from .client import AsyncTraCSS, TraCSS/from .client import AsyncTraCSS, RawResponse, TraCSS/' \
	    sdks/python/tracss/__init__.py
	# No longer apply UP modernizations; they'd introduce discrepancies between the generated
	# and hand-written code and the docstrings.
	# @# --exit-zero: apply safe UP modernizations but don't fail when some violations
	# @# require unsafe fixes or Python 3.12+ syntax (UP040/UP042/UP046/UP047).
	# uv run ruff check --fix --select UP --exit-zero --config 'lint.per-file-ignores={}' sdks/python/tracss/


.PHONY: docs-dev
docs-dev: ## Start local docs preview server at localhost:3000
	fern docs dev

.PHONY: docs-preview
docs-preview: ## Generate shareable docs preview URL (requires FERN_TOKEN or fern login)
	fern generate --docs --preview


.PHONY: fern-stop
fern-stop: ## Stop any background fern docs server
	-pkill -f "fern docs" 2>/dev/null || true
	@printf '\n'


.PHONY: install
install: ## Install workspace dependencies
	uv sync

LINT_TARGETS := sdks/python/tracss/client.py tests/

.PHONY: lint
lint: ## Lint + format check (hand-written files only)
	uv run ruff check $(LINT_TARGETS)
	uv run ruff format --check $(LINT_TARGETS)

format: ## Auto-fix lint + formatting (hand-written files only)
	uv run ruff format $(LINT_TARGETS)
	uv run ruff check --fix $(LINT_TARGETS)
.PHONY: format

.PHONY: pre-commit
pre-commit: ## Run all pre-commit hooks against all files
	uv run pre-commit run --all-files

.PHONY: typecheck
typecheck: ## Run mypy on hand-written files
	uv run mypy sdks/python/tracss/client.py tests/

.PHONY: test
test: ## Run unit tests with coverage
	uv run pytest tests/unit/ -v --cov=tracss.client --cov-report=term-missing --cov-fail-under=90


SUBSCRIBER_PORT ?= 4010
BULKDATA_PORT   ?= 4011
METADATA_PORT   ?= 4012

.PHONY: prism-install
prism-install: ## Install Prism mock server globally (run once before prism-all)
	npm install -g @stoplight/prism-cli@5.15.11

.PHONY: prism-subscriber
prism-subscriber: ## Start Prism mock server for subscriber (defaults to port 4010)
	prism mock fern/openapi/subscriber/openapi.json --port $(SUBSCRIBER_PORT)

.PHONY: prism-bulkdata
prism-bulkdata: ## Start Prism mock server for bulkdata (defaults to port 4011)
	prism mock fern/openapi/bulk_data/openapi.json --port $(BULKDATA_PORT)

.PHONY: prism-metadata
prism-metadata: ## Start Prism mock server for metadata (defaults to port 4012)
	prism mock fern/openapi/metadata/openapi.json --port $(METADATA_PORT)

.PHONY: prism-all
prism-all: ## Start all three Prism mock servers in the background and wait for readiness
	@command -v prism > /dev/null 2>&1 || { echo "Prism not found. Run: make prism-install" >&2; exit 1; }
	@rm -f .prism.pids
	@for spec_port in \
		"fern/openapi/subscriber/openapi.json:::$(SUBSCRIBER_PORT)" \
		"fern/openapi/bulk_data/openapi.json:::$(BULKDATA_PORT)" \
		"fern/openapi/metadata/openapi.json:::$(METADATA_PORT)"; do \
		spec=$$(echo $$spec_port | cut -d: -f1); \
		port=$$(echo $$spec_port | cut -d: -f4-); \
		if ! curl -s --max-time 0.5 http://localhost:$$port > /dev/null 2>&1; then \
			prism mock "$$spec" --port $$port > /dev/null 2>&1 & \
			echo $$! >> .prism.pids; \
		fi; \
	done
	@for port in $(SUBSCRIBER_PORT) $(BULKDATA_PORT) $(METADATA_PORT); do \
		timeout 60 bash -c \
			"until curl -s --max-time 2 http://127.0.0.1:$$port > /dev/null 2>&1; do sleep 0.5; done" \
			|| { echo "Prism did not start on port $$port" >&2; exit 1; }; \
	done

.PHONY: prism-stop
prism-stop: ## Stop all Prism mock servers
	@if [ -f .prism.pids ]; then \
		xargs kill < .prism.pids 2>/dev/null || true; \
		rm -f .prism.pids; \
	fi
	@printf '\n'


.PHONY: integration
integration: ## Run integration tests (requires prism-all running)
	TRACSS_SUBSCRIBER_URL=http://localhost:$(SUBSCRIBER_PORT) \
	TRACSS_BULKDATA_URL=http://localhost:$(BULKDATA_PORT) \
	TRACSS_METADATA_URL=http://localhost:$(METADATA_PORT) \
	TRACSS_CLIENT_ID=fake \
	TRACSS_CLIENT_SECRET=fake \
	uv run pytest tests/integration/ -v --no-cov


.PHONY: build
build: ## Build distribution wheel and validate with twine
	uv build --package tracss
	uv run twine check dist/*

.PHONY: publish
publish: build ## Publish to PyPI via OIDC (CI) or UV_PUBLISH_TOKEN (local)
	uv publish

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
	uv run pip-audit --vulnerability-service osv

.PHONY: coverage
coverage: ## Generate HTML coverage report (open htmlcov/index.html)
	uv run pytest tests/unit/ --cov=tracss.client --cov-report=html
