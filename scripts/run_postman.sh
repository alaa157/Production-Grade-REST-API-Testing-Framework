#!/usr/bin/env bash
set -euo pipefail
# Run Postman collection via Newman (Phase 11).
# Usage: ./scripts/run_postman.sh [--ci]
#   --ci  also emit JUnit XML to reports/newman-results.xml

cd "$(dirname "$0")/.."

COLLECTION="postman/collections/restful-booker-api.postman_collection.json"
ENVIRONMENT="postman/environments/restful-booker.postman_environment.json"

if [ -x "node_modules/.bin/newman" ]; then
  NEWMAN="node_modules/.bin/newman"   # pinned local install (npm ci)
elif command -v newman >/dev/null 2>&1; then
  NEWMAN="newman"
else
  echo "Newman not installed. Run: npm ci  (or: npm install -g newman)"
  exit 1
fi

ARGS=("run" "$COLLECTION")
if [ -f "$ENVIRONMENT" ]; then
  ARGS+=("-e" "$ENVIRONMENT")
fi
if [ "${1:-}" = "--ci" ]; then
  ARGS+=("-r" "cli,junit" "--reporter-junit-export" "reports/newman-results.xml")
fi

"$NEWMAN" "${ARGS[@]}"
