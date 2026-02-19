#!/usr/bin/env bash
set -euo pipefail

# Render Cron job entrypoint for PostgreSQL backup.
# Required env:
#   DATABASE_URL
# Optional env:
#   DB_BACKUP_DIR (default: /tmp/db_backups)

export DJANGO_SETTINGS_MODULE="Project_shivshakti.settings"
export DJANGO_ENV="production"

BACKUP_DIR="${DB_BACKUP_DIR:-/tmp/db_backups}"
mkdir -p "$BACKUP_DIR"

python manage.py backup_database --output-dir "$BACKUP_DIR"

# Optional S3-compatible upload (uncomment if AWS CLI is configured):
# aws s3 cp "$BACKUP_DIR" "s3://your-backup-bucket/shivshakti/" --recursive
