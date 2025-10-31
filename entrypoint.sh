
#!/bin/busybox sh
set -e

echo "Entrypoint: attempting to run create_tables for detected service (if available)"

# Determine service module from command or env var
SERVICE_MODULE=""
for arg in "$@"; do
  case "$arg" in
    *service_users.*)
      SERVICE_MODULE="service_users"
      break
      ;;
    *service_membership.*)
      SERVICE_MODULE="service_membership"
      break
      ;;
    *service_providers.*)
      SERVICE_MODULE="service_providers"
      break
      ;;
    *service_catalog.*)
      SERVICE_MODULE="service_catalog"
      break
      ;;
    *service_access.*)
      SERVICE_MODULE="service_access"
      break
      ;;
  esac
done

# Allow override from environment
if [ -n "${SERVICE_MODULE_OVERRIDE}" ]; then
  SERVICE_MODULE="${SERVICE_MODULE_OVERRIDE}"
fi

if [ -n "${SERVICE_MODULE}" ]; then
  echo "Detected service module: ${SERVICE_MODULE}"
else
  echo "No service module detected in command args"
fi

# Try to run create_tables with database creation
python - <<'EOF'
import os
import time
import sys
import psycopg2
from psycopg2 import errors

def wait_for_postgres(host, port, user, password, max_attempts=15):
    for i in range(max_attempts):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database="postgres"  # Connect to default db first
            )
            conn.close()
            return True
        except Exception as e:
            print(f"Waiting for PostgreSQL to be ready (attempt {i+1}): {e}")
            time.sleep(2)
    return False

def ensure_database_exists(host, port, user, password, dbname):
    try:
        # Connect to default database first
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Try to create database if it doesn't exist
        try:
            cur.execute(f'CREATE DATABASE {dbname}')
            print(f"Created database {dbname}")
        except errors.DuplicateDatabase:
            print(f"Database {dbname} already exists")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error ensuring database exists: {e}")
        return False

def try_create_tables(module_name):
    try:
        # Get DB connection info from environment
        host = os.environ.get('DB_HOST', 'localhost')
        port = os.environ.get('DB_PORT', '5432')
        user = os.environ.get('DB_USER', 'postgres')
        password = os.environ.get('DB_PASSWORD', 'password')
        dbname = os.environ.get('DB_NAME', module_name.split('_')[-1])
        
        print(f"Waiting for database {host}:{port} to be ready...")
        if not wait_for_postgres(host, port, user, password):
            print("Database not ready after maximum retries")
            return False
            
        print(f"Ensuring database {dbname} exists...")
        if not ensure_database_exists(host, port, user, password, dbname):
            print("Failed to create/verify database")
            return False
            
        print(f"Importing {module_name}.db...")
        mod = __import__(f"{module_name}.db", fromlist=['create_tables'])
        create = getattr(mod, 'create_tables', None)
        if not callable(create):
            print(f'No callable create_tables in {module_name}.db')
            return False
            
        print(f"Running create_tables...")
        create()
        print(f'{module_name}.db.create_tables succeeded')
        return True
    except Exception as e:
        print(f'Error in try_create_tables: {e}')
        return False

# Get module from env or try known modules
module = os.environ.get('SERVICE_MODULE')
if module:
    try_create_tables(module)
else:
    # Try each known module
    for mod in ['service_users', 'service_reservations', 'service_membership']:
        if try_create_tables(mod):
            break
EOF

echo "Entrypoint: launching command -> $@"
exec "$@"
