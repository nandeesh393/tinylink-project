#!/usr/bin/env bash
set -euo pipefail

# Simple autograder-style tests for TinyLink (Django)
# Usage:
#  - Ensure server is running: python manage.py runserver 0.0.0.0:8000
#  - Run: ./curl_tests.sh
# Requires: curl, jq (jq optional; script will work without it but output will be raw JSON)

BASE="${BASE:-http://localhost:8000}"
echo "Using BASE=$BASE"

echo
echo "1) Health check -> GET /healthz"
curl -i "${BASE}/healthz" || true
echo
echo "---------------------------------------------"

echo
echo "2) Create a new link (no custom code)"
CREATE_OUTPUT=$(curl -s -X POST "${BASE}/api/links" -H "Content-Type:application/json" -d '{"target":"https://google.com"}')
echo "Create response:"
echo "${CREATE_OUTPUT}"
echo

# extract code
CODE=$(echo "${CREATE_OUTPUT}" | jq -r '.code' 2>/dev/null || echo "")
if [ -z "${CODE}" ] || [ "${CODE}" = "null" ]; then
  echo "ERROR: could not extract code from create response. Exiting."
  exit 1
fi
echo "Created code: ${CODE}"

echo
echo "---------------------------------------------"
echo
echo "3) Get single link -> GET /api/links/${CODE}"
curl -i "${BASE}/api/links/${CODE}" || true
echo
echo "---------------------------------------------"

echo
echo "4) Trigger redirect -> GET /${CODE} (should respond 302 with Location header)"
curl -v --max-redirs 0 "${BASE}/${CODE}" 2>&1 | sed -n '1,200p' || true
echo
echo "---------------------------------------------"

echo
echo "5) Confirm clicks increment -> GET /api/links/${CODE}"
curl -i "${BASE}/api/links/${CODE}" || true
echo
echo "---------------------------------------------"

echo
echo "6) Delete the link -> DELETE /api/links/${CODE}"
curl -i -X DELETE "${BASE}/api/links/${CODE}" || true
echo
echo "7) Confirm redirect returns 404 after delete"
curl -i "${BASE}/${CODE}" || true
echo
echo "---------------------------------------------"
echo "All tests completed."
