#!/bin/bash

# Database configuration
DB_NAME="notification_service_test"
DB_USER="notification_service_user"
DB_PASSWORD="hunter2butbetter"

echo "Setting up test database..."

# Create user if not exists
psql postgres -c "DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;"

# Create database if not exists
psql postgres -c "CREATE DATABASE $DB_NAME WITH OWNER = $DB_USER;" 2>/dev/null || echo "Database already exists"

# Grant all privileges
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
psql -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
psql -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;"

echo "Test database setup complete!"