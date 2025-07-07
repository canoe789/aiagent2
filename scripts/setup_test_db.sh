#!/bin/bash
# Setup test database for E2E tests

echo "Setting up test database for HELIX E2E tests..."

# Check if PostgreSQL is running
if ! pg_isready; then
    echo "PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Create test database
echo "Creating helix_test database..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS helix_test;"
sudo -u postgres psql -c "CREATE DATABASE helix_test;"

# Grant permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE helix_test TO helix_user;"

echo "Test database setup complete!"