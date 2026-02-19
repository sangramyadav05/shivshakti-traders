import os
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create a PostgreSQL backup using pg_dump.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            default=os.getenv('DB_BACKUP_DIR', str(Path(settings.BASE_DIR) / 'backups')),
            help='Directory where backup files will be stored.',
        )

    def handle(self, *args, **options):
        database_url = os.getenv('DATABASE_URL', '').strip()
        if not database_url:
            raise CommandError('DATABASE_URL is not set. Cannot run backup.')

        parsed = urlparse(database_url)
        if parsed.scheme not in ('postgres', 'postgresql'):
            raise CommandError('backup_database supports PostgreSQL DATABASE_URL only.')

        db_name = parsed.path.lstrip('/')
        db_user = parsed.username or ''
        db_password = parsed.password or ''
        db_host = parsed.hostname or 'localhost'
        db_port = str(parsed.port or 5432)

        output_dir = Path(options['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{db_name}_{timestamp}.sql"
        backup_path = output_dir / filename

        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password

        command = [
            'pg_dump',
            '--no-owner',
            '--no-privileges',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-d', db_name,
            '-f', str(backup_path),
        ]

        self.stdout.write(self.style.NOTICE(f'Starting backup for database: {db_name}'))
        self.stdout.write(self.style.NOTICE(f'Output file: {backup_path}'))

        try:
            completed = subprocess.run(
                command,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError as exc:
            raise CommandError('pg_dump not found. Install PostgreSQL client tools on this environment.') from exc
        except Exception as exc:
            raise CommandError(f'Unexpected backup error: {exc}') from exc

        if completed.returncode != 0:
            error_output = (completed.stderr or completed.stdout or '').strip()
            self.stderr.write(self.style.ERROR(f'Backup failed: {error_output}'))
            raise CommandError('Database backup command failed.')

        file_size = backup_path.stat().st_size
        self.stdout.write(self.style.SUCCESS(f'Backup completed successfully: {backup_path} ({file_size} bytes)'))

        self.stdout.write(self.style.NOTICE('Local storage simulation complete.'))
        self.stdout.write(self.style.NOTICE('For S3-compatible storage: upload this file in a post-backup step (AWS CLI/rclone/boto3).'))
