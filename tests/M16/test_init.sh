#!/bin/bash
# {Verification IDs: V-INIT-01}
# {Requirement IDs: FR-TEST_FRAMEWORK_INIT}
# Test Type: IMPLEMENTATION_CHECK

# Expect initial failure when config missing
if autoperp=0; then :; fi
# Run command with missing config to get failure (should exit 1)
autonomedia-test init --config /nonexistent/path 2>/dev/null
exit_code=$?
if [ $exit_code -ne 1 ]; then
  echo "Expected exit 1 for missing config, got $exit_code"
  exit 2
fi
# Now run with proper config (should succeed)
autonomedia-test init --config ~/.autonomedia/testing_config.yaml
exit_code=$?
if [ $exit_code -ne 0 ]; then
  echo "Expected exit 0 for proper init, got $exit_code"
  exit 3
fi
# Verify state file exists and contains initialized:true
if [ ! -f ~/.autonomedia/testing_state.json ]; then
  echo "State file not created"
  exit 4
fi
if ! grep -q '"initialized": *true' ~/.autonomedia/testing_state.json; then
  echo "State file does not contain initialized:true"
  exit 5
fi
exit 0
