#!/bin/bash
# {Verification IDs: VER-M18S1V-03}
# {Requirement IDs: FR-DASHBOARD_DATA_BINDING}
# Test Type: IMPLEMENTATION_CHECK

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
API_PATH="/api/health"
DASHBOARD_PATH="/health"

echo "Testing dashboard data binding..."

# Step 1: Fetch health status from API
echo "Fetching health status from API..."
if curl -s -o /tmp/health_response.json "$BASE_URL$API_PATH" > /dev/null 2>&1; then
    echo "PASS: API endpoint accessible"
else
    echo "FAIL: Unable to fetch health status from API"
    exit 1
fi

# Step 2: Parse health status values
echo "Parsing health status values..."

COMPONENTS=("database" "runtime" "tests" "src")
VALID_VALUES=("healthy" "unhealthy")

for component in "${COMPONENTS[@]}"; do
    status=$(jq -r --arg c "$component" '.[$c]' /tmp/health_response.json 2>/dev/null || echo "")

    if [ -z "$status" ]; then
        echo "FAIL: No status found for component '$component'"
        exit 1
    fi

    # Check if status is valid
    valid=false
    for value in "${VALID_VALUES[@]}"; do
        if [ "$status" == "$value" ]; then
            valid=true
            break
        fi
    done

    if [ "$valid" == false ]; then
        echo "FAIL: Invalid status value '$status' for component '$component'"
        exit 1
    fi

    echo "  - $component: $status"
done

# Step 3: Validate dashboard HTML contains indicators matching API values
echo "Validating dashboard HTML status indicators..."

if ! curl -s -o /tmp/dashboard_response.html "$BASE_URL$DASHBOARD_PATH" > /dev/null 2>&1; then
    echo "FAIL: Unable to fetch dashboard HTML"
    exit 1
fi

# Check for status indicators for each component
for component in "${COMPONENTS[@]}"; do
    status=$(jq -r --arg c "$component" '.[$c]' /tmp/health_response.json 2>/dev/null || echo "")

    if [ "$status" == "healthy" ]; then
        indicator_pattern="<[^>]*$component[^>]*(class|id)=[^>]*healthy[^>]*>"
    elif [ "$status" == "unhealthy" ]; then
        indicator_pattern="<[^>]*$component[^>]*(class|id)=[^>]*unhealthy[^>]*>"
    else
        echo "WARN: Unexpected status '$status' for component '$component', skipping indicator check"
        continue
    fi

    if ! grep -qE "$indicator_pattern" /tmp/dashboard_response.html; then
        echo "FAIL: Dashboard HTML missing status indicator for component '$component' with status '$status'"
        exit 1
    fi

    echo "  - $component indicator found (status: $status)"
done

echo "PASS: All component status indicators found in dashboard HTML"

# Clean up
rm -f /tmp/health_response.json /tmp/dashboard_response.html

exit 0
