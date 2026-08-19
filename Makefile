.PHONY: build watch check

FRONTEND_DIR := src/celestialflow_web
TSC := $(FRONTEND_DIR)/node_modules/.bin/tsc
TSCONFIG := $(FRONTEND_DIR)/tsconfig.json

build:
	$(TSC) -p $(TSCONFIG)

watch:
	$(TSC) -p $(TSCONFIG) --watch

check:
	$(TSC) -p $(TSCONFIG) --noEmit
