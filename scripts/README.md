# AI-GAPSIM Scripts

This directory contains utility scripts for managing the AI-GAPSIM application.

## Database Management

### `init_db.sh`

Initializes or resets the database with the initial schema and data.

```bash
./init_db.sh
```

### `backup.sh`

Creates a backup of the database and data files.

```bash
./backup.sh
```

Backups are stored in the `backups` directory with timestamps.

### `restore.sh`

Restores the database and data files from a backup.

```bash
./restore.sh <db_backup_file> <data_backup_file>
```

Example:
```bash
./restore.sh backups/db_backup_20230101_120000.sql backups/data_backup_20230101_120000.tar.gz
```

## Application Management

### `start_app.sh`

Starts the application in development or production mode.

```bash
./start_app.sh [dev|prod]
```

If no mode is specified, it defaults to development mode.

### `deploy.sh`

Deploys the application to production.

```bash
./deploy.sh
```

This script requires a `.env.prod` file with production settings.

### `update.sh`

Updates the application to the latest version.

```bash
./update.sh
```

This script pulls the latest changes from the repository, rebuilds the application, and runs database migrations.

### `monitor.sh`

Monitors the application.

```bash
./monitor.sh [logs|status|stats]
```

Options:
- `logs` - Show logs from all containers
- `status` - Show status of all containers (default)
- `stats` - Show resource usage statistics

### `cleanup.sh`

Cleans up the environment.

```bash
./cleanup.sh [--all]
```

If `--all` is specified, it removes all containers, volumes, and data. Otherwise, it only removes containers and networks.

## Data Management

### `generate_sample_data.sh`

Generates sample data for testing.

```bash
./generate_sample_data.sh
```

## Testing

### `run_tests.sh`

Runs tests for the backend, frontend, or both.

```bash
./run_tests.sh [backend|frontend|all]
```

If no component is specified, it defaults to running all tests.
