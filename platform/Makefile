.PHONY: clean lint test size
clean:
	rm -rf platform/web/.next platform/web/dist platform/mobile/.expo platform/mobile/dist platform/**/coverage || true
lint:
	@if [ -f platform/web/package.json ]; then (cd platform/web && corepack enable && pnpm i && pnpm eslint .); fi; \
	if [ -f platform/mobile/package.json ]; then (cd platform/mobile && corepack enable && pnpm i && pnpm eslint .); fi; \
	if [ -d platform/api ]; then (cd platform/api && python3 -m venv .venv && . .venv/bin/activate && pip install -q ruff && ruff check . && ruff format --check .); fi
test:
	@if [ -f platform/web/package.json ]; then (cd platform/web && pnpm -s test || true); fi; \
	if [ -f platform/mobile/package.json ]; then (cd platform/mobile && pnpm -s test || true); fi; \
	if [ -d platform/api ]; then (cd platform/api && . .venv/bin/activate && pytest -q || true); fi
size:
	cd platform && bash scripts/guard-big-files.sh
