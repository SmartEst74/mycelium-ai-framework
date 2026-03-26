.PHONY: setup benchmark test help

help:
	@echo "Mycelium AI Framework — Quick Commands"
	@echo ""
	@echo "  make setup      Full setup (no install needed, Node.js built-in)"
	@echo "  make test       Run unit tests (11 tests)"
	@echo "  make benchmark  Run solo vs colonial benchmark"
	@echo ""
	@echo "Quick start:"
	@echo "  git clone https://github.com/SmartEst74/mycelium-ai-framework.git"
	@echo "  cd mycelium-ai-framework"
	@echo "  make test"

setup:
	@echo "No install needed. Node.js 22+ is all you need."
	@echo ""
	@echo "Verify:"
	@echo "  node --version   # must be >= 22"
	@echo "  make test"

test:
	node --experimental-sqlite --test tests/test.mjs

benchmark:
	node --experimental-sqlite benchmarks/colonial_memory_bench.mjs
