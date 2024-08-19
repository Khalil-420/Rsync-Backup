# FastAPI Rsync Backup Microservice

This microservice is designed to facilitate automated backups using rsync and Docker Compose, managed through FastAPI. It includes functionality to schedule backups, monitor rsync status, and manage servers.


## Features

- **Start Backup**: Initiate a backup process for the configured servers.
- **Check Backup Status**: Retrieve the current status of the rsync backup process.
- **Add Server**: Add a new server to the database for backup.
- **Remove Server**: Remove a server from the database.
- **List Servers**: List all servers currently in the database.
- **Update Server**: Update the configuration of an existing server.
- **Start Cron Job**: Schedule a cron job to run the backup at specified times.
- **Stop Cron Job**: Remove the scheduled cron job.
- **Email Notifications**: Automatically send email notifications in case of errors during backup or status checks.




