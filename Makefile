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
	tmp=fern/openapi/$$name/openapi.json.tmp; \
	if curl -fsSL --connect-timeout 10 --max-time 30 --retry 3 --retry-delay 2 --retry-all-errors "$$url" -o "$$tmp" \
		&& python3 -m json.tool "$$tmp" > /dev/null 2>&1; then \
		mv "$$tmp" fern/openapi/$$name/openapi.json; \
	else \
		rm -f "$$tmp"; \
		echo "  ! failed to fetch $$name from $$url (unreachable, error, or non-JSON response)" >&2; \
		exit 1; \
	fi; \
	done
	# Apply local spec patches (subscriber 'fields' optional, metadata CSV upload body).
	# Logic lives in scripts/patch_specs.py so it can be unit-tested and fail with a
	# clear message naming what changed - see tests/unit/test_patch_specs.py.
	@python3 scripts/patch_specs.py
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
	@# Same fix for README.md and reference.md: Fern usage examples show
	@# token="<token>", which raises TypeError against the public TraCSS constructor
	@# (it forwards **kwargs into BaseTraCSS(token=...) -> duplicate 'token' argument).
	@sed -i 's/token="<token>"/client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET"/g' \
	    sdks/python/tracss/README.md \
	    sdks/python/tracss/reference.md
	@# Wire __version__ into the lazy-loader so `tracss.__version__` works at runtime.
	@# _version.py is protected by .fernignore; __init__.py is regenerated each run.
	@sed -i 's/"subscriber": ".subscriber"}/"subscriber": ".subscriber", "__version__": "._version"}/' \
	    sdks/python/tracss/__init__.py
	@# Expose hand-written RawResponse (from client.py) via the top-level package.
	@# Three patches: _dynamic_imports dict, __all__ list, TYPE_CHECKING import.
	@grep -qF '"RawResponse": ".client", "TraCSS"' sdks/python/tracss/__init__.py || \
	    sed -i 's/"TraCSS": ".client"/"RawResponse": ".client", "TraCSS": ".client"/' \
	        sdks/python/tracss/__init__.py
	@# Idempotency guards: these seds run every invocation, so without a guard a
	@# re-run would append "RawResponse" to __all__ a second time (duplicate entry).
	@grep -qF '"RawResponse", "TraCSS", "TraCSSEnvironment"' sdks/python/tracss/__init__.py || \
	    sed -i 's/"TraCSS", "TraCSSEnvironment"/"RawResponse", "TraCSS", "TraCSSEnvironment"/' \
	        sdks/python/tracss/__init__.py
	@grep -qF 'from .client import AsyncTraCSS, RawResponse, TraCSS' sdks/python/tracss/__init__.py || \
	    sed -i 's/from .client import AsyncTraCSS, TraCSS/from .client import AsyncTraCSS, RawResponse, TraCSS/' \
	        sdks/python/tracss/__init__.py
	@# Verify that all patches actually matched something.  sed exits 0 even when
	@# it replaces nothing, so we check the expected strings are present afterwards.
	@python3 -c "\
import sys, pathlib; \
init = pathlib.Path('sdks/python/tracss/__init__.py').read_text(); \
errors = []; \
'\"RawResponse\"' in init or errors.append('RawResponse export patch (post-generate step 2) failed'); \
init.count('\"RawResponse\"') == 2 or errors.append(f'RawResponse should appear exactly twice in __init__.py (_dynamic_imports + __all__), found {init.count(chr(34)+\"RawResponse\"+chr(34))}'); \
'\"__version__\"' in init or errors.append('__version__ patch (post-generate step 1) failed'); \
aio = pathlib.Path('sdks/python/tracss/tests/test_aiohttp_autodetect.py'); \
(not aio.exists() or 'open-space-collective' not in aio.read_text()) or errors.append('org-name patch (post-generate step 0) failed'); \
[('token=\"<token>\"' not in pathlib.Path(p).read_text()) or errors.append(f'{p}: token=<token> doc fix failed') for p in ('sdks/python/tracss/README.md','sdks/python/tracss/reference.md')]; \
errors and (print('post-generate verification failed:\n  ' + '\n  '.join(errors), file=sys.stderr) or sys.exit(1)); \
print('post-generate patches verified.')"
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

LINT_TARGETS   := sdks/python/tracss/client.py tests/
FORMAT_TARGETS := sdks/python/tracss/ tests/

.PHONY: lint
lint: ## Lint + format check
	uv run ruff check $(LINT_TARGETS)
	uv run ruff format --check $(FORMAT_TARGETS)

format: ## Auto-fix lint + format all Python files
	uv run ruff format $(FORMAT_TARGETS)
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
