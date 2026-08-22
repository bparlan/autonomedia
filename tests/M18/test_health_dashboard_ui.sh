#!/bin/bash
# {Verification IDs: VER-M18S1V-02}
# {Requirement IDs: FR-DASHBOARD_UI_INIT}
# Test Type: IMPLEMENTATION_CHECK

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
DASHBOARD_PATH="/health"

echo "Testing GET $BASE_URL$DASHBOARD_PATH dashboard page..."

# Capture curl exit code explicitly
if curl -s -o /tmp/dashboard_response.html -w "%{http_code}" "$BASE_URL$DASHBOARD_PATH" > /tmp/curl_exit.txt 2>/dev/null; then
    HTTP_CODE=$(cat /tmp/curl_exit.txt)
else
    HTTP_CODE=127
fi

if [ "$HTTP_CODE" != "200" ]; then
    echo "FAIL: Expected HTTP 200, got $HTTP_CODE"
    exit 1
fi

echo "PASS: HTTP $HTTP_CODE received"

# Validate HTML contains dashboard container
echo "Validating dashboard container element..."

if ! grep -qE '(<div[^>]*id="health-dashboard"[^>]*>|<div[^>]*class="health-dashboard"[^>]*>)' /tmp/dashboard_response.html; then
    echo "FAIL: Dashboard container element not found (expected id='health-dashboard' or class='health-dashboard')"
    exit 1
fi

echo "PASS: Dashboard container element found"

# Validate HTML contains structure indicating a dashboard (basic checks)
echo "Validating dashboard structure..."

if ! grep -qE '(<h1[^>]*>|<h2[^>]*>|<title>.*Health.*</title>)' /tmp/dashboard_response.html; then
    echo "WARN: No header/title elements found in dashboard HTML"
    # This is a warning, not a failure, as structure could vary
fi

# Clean up
rm -f /tmp/dashboard_response.html /tmp/curl_exit.txt

exit 0
