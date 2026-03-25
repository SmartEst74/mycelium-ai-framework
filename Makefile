.PHONY: setup demo benchmark test help

help:
	@echo "Mycelium AI Framework — Quick Commands"
	@echo ""
	@echo "  make setup      Full setup: install deps + bootstrap knowledge + run demo"
	@echo "  make demo       Run the E2E event bus demo"
	@echo "  make benchmark  Run solo vs colonial benchmark"
	@echo "  make test       Run unit tests"
	@echo ""
	@echo "Quick start:"
	@echo "  git clone https://github.com/SmartEst74/mycelium-ai-framework.git"
	@echo "  cd mycelium-ai-framework"
	@echo "  make setup"

setup: ## Full setup for a fresh OpenClaw instance
	@echo "=== Installing dependencies ==="
	pip install -e .
	@echo ""
	@echo "=== Importing framework knowledge into QMD memory ==="
	bash scripts/bootstrap-knowledge.sh
	@echo ""
	@echo "=== Setup complete! ==="
	@echo ""
	@echo "Next steps:"
	@echo "  1. Read docs/LESSONS.md for the full knowledge base"
	@echo "  2. Set up your OpenClaw config:"
	@echo "     openclaw config.patch '{\"agents\":{\"defaults\":{\"contextTokens\":120000}}}'"
	@echo "  3. Install LCM plugin:"
	@echo "     openclaw plugins install @martian-engineering/lossless-claw"

demo: ## Run the E2E event bus demo
	python3 benchmarks/e2e_demo.py

benchmark: ## Run solo vs colonial benchmark
	python3 benchmarks/run_benchmark.py

test: ## Run unit tests
	pytest tests/ -v

clean: ## Clean up demo artifacts
	rm -f benchmarks/lcm_demo.db
	rm -f benchmarks/.rhizomorph/*/lessons.json
