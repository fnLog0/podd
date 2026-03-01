#!/usr/bin/env bash
set -e

DB_NAME="podd-db"

TABLES=(
  "oauth_accounts"
  "sessions"
  "users"
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "Cleaning local D1 database: $DB_NAME"
echo "---"

for table in "${TABLES[@]}"; do
  echo "Dropping $table ..."
  npx wrangler d1 execute "$DB_NAME" --local --command="DROP TABLE IF EXISTS $table;"
done

echo "---"
echo "Done. Local D1 tables dropped."
echo "Run 'pnpm db:import' to re-create them."
