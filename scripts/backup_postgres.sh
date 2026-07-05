#!/usr/bin/env bash
set -euo pipefail

timestamp="$(date +%Y%m%d-%H%M%S)"
mkdir -p backups
docker compose exec -T db pg_dump -U grantatlas grantatlas > "backups/grantatlas-${timestamp}.sql"
echo "Created backups/grantatlas-${timestamp}.sql"

