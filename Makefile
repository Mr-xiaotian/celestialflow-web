.PHONY: build watch check serve

FRONTEND_DIR := src/celestialflow_web
TSC := node $(FRONTEND_DIR)/node_modules/typescript/bin/tsc
TSCONFIG := $(FRONTEND_DIR)/tsconfig.json

build:
	$(TSC) -p $(TSCONFIG)

watch:
	$(TSC) -p $(TSCONFIG) --watch

check:
	$(TSC) -p $(TSCONFIG) --noEmit

serve:
	uv run celestialflow-web --port 5005
