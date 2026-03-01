#!/usr/bin/env bash
set -e

DB_NAME="podd-db"
SCHEMA_DIR="src/db"

SCHEMAS=(
  "user/schema.sql"
  "session/schema.sql"
  "oauth/schema.sql"
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "Importing D1 SQL into local database: $DB_NAME"
echo "---"

for rel in "${SCHEMAS[@]}"; do
  file="$SCHEMA_DIR/$rel"
  if [[ ! -f "$file" ]]; then
    echo "Error: $file not found"
    exit 1
  fi
  echo "Running $file ..."
  npx wrangler d1 execute "$DB_NAME" --local --file="$file"
done

echo "---"
echo "Done. Local D1 schema is up to date."
