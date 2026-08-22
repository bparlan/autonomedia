#!/bin/bash
# {Verification IDs: VR-DBD-SOURCE-002}
# {Requirement IDs: FR-DASHBOARD_DATA_SOURCE}
# Test Type: IMPLEMENTATION_CHECK

    # Test /api/health endpoint returns 200 OK with valid JSON.

set -euo pipefail

# Expected JSON structure
EXPECTED_KEYS=("database" "runtime" "tests" "src")

# Test 1: Make HTTP request to /api/health endpoint
echo "Testing /api/health endpoint..."
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/health)

# Extract HTTP status code
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

# Verify HTTP status code is 200
if [ "$HTTP_CODE" != "200" ]; then
    echo "FAIL: Expected HTTP 200, got $HTTP_CODE"
    echo "Response body: $BODY"
    exit 1
fi

echo "PASS: HTTP status is 200"

# Verify response is valid JSON
if ! echo "$BODY" | jq -e . > /dev/null 2>&1; then
    echo "FAIL: Response is not valid JSON"
    echo "Response body: $BODY"
    exit 1
fi

echo "PASS: Response is valid JSON"

# Verify all required keys exist
for KEY in "${EXPECTED_KEYS[@]}"; do
    if ! echo "$BODY" | jq -e ".[\"$KEY\"]" > /dev/null 2>&1; then
        echo "FAIL: Missing required key '$KEY'"
        echo "Response body: $BODY"
        exit 1
    fi
    echo "PASS: Key '$KEY' exists"
done

# Verify each key value is either "healthy" or "unhealthy"
for KEY in "${EXPECTED_KEYS[@]}"; do
    VALUE=$(echo "$BODY" | jq -r ".[\"$KEY\"]")
    if [ "$VALUE" != "healthy" ] && [ "$VALUE" != "unhealthy" ]; then
        echo "FAIL: Key '$KEY' has invalid value '$VALUE'"
        echo "Response body: $BODY"
        exit 1
    fi
    echo "PASS: Key '$KEY' has valid value '$VALUE'"
done

echo ""
echo "All tests passed"
