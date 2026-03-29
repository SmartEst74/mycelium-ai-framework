.PHONY: setup benchmark test test-rust test-all help dashboard

help:
	@echo "Mycelium AI Framework — Quick Commands"
	@echo ""
	@echo "  make setup        Full setup (no install needed, Node.js built-in)"
	@echo "  make test         Run Node.js unit tests"
	@echo "  make test-rust    Run Rust neural-bridge tests"
	@echo "  make test-all     Run all tests (Node + Rust)"
	@echo "  make benchmark    Run solo vs colonial benchmark"
	@echo "  make dashboard    Open Spore dashboard (requires spore-server running)"
	@echo ""
	@echo "Quick start:"
	@echo "  git clone https://github.com/SmartEst74/mycelium-ai-framework.git"
	@echo "  cd mycelium-ai-framework"
	@echo "  make test-all"

setup:
	@echo "No install needed. Node.js 22+ is all you need."
	@echo "For neural-bridge: install Rust toolchain (rustup.rs)"
	@echo ""
	@echo "Verify:"
	@echo "  node --version   # must be >= 22"
	@echo "  cargo --version  # for neural-bridge"
	@echo "  make test-all"

test:
	node --experimental-sqlite --test tests/test.mjs

test-rust:
	cd neural-bridge && cargo test

test-all: test test-rust

benchmark:
	node --experimental-sqlite benchmarks/colonial_memory_bench.mjs

dashboard:
	@echo "Starting spore-server on ws://localhost:9001 ..."
	@cd neural-bridge && cargo run --bin spore-server &
	@sleep 1
	@open dashboard/index.html 2>/dev/null || xdg-open dashboard/index.html 2>/dev/null || echo "Open dashboard/index.html in your browser"
