Docker image with posgres tools to manage backup and restore

    sudo docker run --rm -i \
        --link postgres_image:db \
        jobiols/dbtools:1.5.0 \
            --db_name bukito_prod \
            --backupfile mybackup.zip
            --days-to-keep 7
            --backup

optional arguments:
  -h, --help            show this help message and exit
  --db-name DB_NAME     Name of the database to restore to or to back up from
  --backupfile BACKUPFILE
                        The backup filename. On restore, defaults to the last backup file. On backup, defaults to a filename with a timestamp
  --days-to-keep DAYS_TO_KEEP
                        Number of days to keep backups also called retention days
  --restore             Restore database
  --backup              Backup database
  --no-neutralize       Make an exact database (no neutralize)
  --project PROJECT     Project to restore
