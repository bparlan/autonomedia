# Justfile - Project Command Runner

# Verify project integrity
verify:
    @echo "Verifying project integrity..."
    @./scripts/verify_no_leak.sh

# Run the worker runtime
run-worker:
    @python3 src/autonomedia/core/worker.py

# Run standard tests
test:
    @pytest
