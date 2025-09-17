# Database Setup Guide

This guide explains how to set up the database for the Anti-Fraud Platform.

## Prerequisites

- PostgreSQL 12+ (for local development) or Supabase account
- Python 3.8+ with asyncpg installed
- Environment variables configured

## Option 1: Supabase (Production/Staging)

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Note your database connection details

### 2. Set Environment Variables

```bash
export SUPABASE_DB_URL="postgresql://postgres:password@db.project.supabase.co:5432/postgres"
export SUPABASE_URL="https://project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"
```

### 3. Run Database Setup

```bash
cd platform/scripts
python setup_supabase_db.py
```

This will:
- Create all required tables
- Set up Row Level Security (RLS)
- Seed initial data
- Verify the setup

## Option 2: Local PostgreSQL (Development)

### 1. Install PostgreSQL

**Windows:**
```bash
# Using Chocolatey
choco install postgresql

# Or download from postgresql.org
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE antifraud_test;
CREATE USER antifraud_user WITH PASSWORD 'antifraud_password';
GRANT ALL PRIVILEGES ON DATABASE antifraud_test TO antifraud_user;
\q
```

### 3. Set Environment Variables

```bash
export SUPABASE_DB_URL="postgresql://antifraud_user:antifraud_password@localhost:5432/antifraud_test"
```

### 4. Run Test Database Setup

```bash
cd platform/scripts
python test_db_setup.py
```

## Option 3: Docker (Quick Start)

### 1. Start PostgreSQL Container

```bash
docker run --name antifraud-postgres \
  -e POSTGRES_DB=antifraud_test \
  -e POSTGRES_USER=antifraud_user \
  -e POSTGRES_PASSWORD=antifraud_password \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Set Environment Variables

```bash
export SUPABASE_DB_URL="postgresql://antifraud_user:antifraud_password@localhost:5432/antifraud_test"
```

### 3. Run Database Setup

```bash
cd platform/scripts
python test_db_setup.py
```

## Verification

### 1. Check Database Health

```bash
curl http://localhost:8000/health/database
```

Expected response:
```json
{
  "status": "healthy",
  "database": "antifraud_test",
  "version": "PostgreSQL 15.0",
  "active_connections": 1,
  "pool_size": 10,
  "pool_idle": 9
}
```

### 2. Check Tables

```bash
# Connect to database
psql $SUPABASE_DB_URL

# List tables
\dt

# Check sample data
SELECT * FROM decision_matrix LIMIT 5;
SELECT * FROM organizations;
```

## Database Schema

### Core Tables

- **organizations** - Multi-tenant organization management
- **projects** - Sub-organizations for fine-grained access control
- **api_keys** - API authentication and permissions
- **events** - Transaction events and user actions
- **decisions** - Fraud detection decisions
- **cases** - Manual review cases
- **decision_matrix** - Rule configuration matrix

### Security Features

- **Row Level Security (RLS)** enabled on all tables
- **API key-based authentication** for all operations
- **Project-based data isolation** for multi-tenancy
- **Audit trails** for all data changes

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if PostgreSQL is running
   - Verify connection string format
   - Check firewall settings

2. **Authentication Failed**
   - Verify username/password
   - Check user permissions
   - Ensure database exists

3. **Permission Denied**
   - Grant proper privileges to user
   - Check RLS policies
   - Verify API key permissions

### Debug Commands

```bash
# Test connection
psql $SUPABASE_DB_URL -c "SELECT version();"

# Check database size
psql $SUPABASE_DB_URL -c "SELECT pg_size_pretty(pg_database_size(current_database()));"

# List active connections
psql $SUPABASE_DB_URL -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

## Next Steps

After database setup:

1. **Start the API server**:
   ```bash
   cd platform/api
   python -m uvicorn src.main:app --reload --port 8000
   ```

2. **Test API endpoints**:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/docs
   ```

3. **Run tests**:
   ```bash
   cd platform/api
   python -m pytest tests/ -v
   ```

4. **Start replay worker**:
   ```bash
   cd platform/api
   python replay_main.py
   ```

## Support

For issues with database setup:

1. Check the logs in the console output
2. Verify environment variables are set correctly
3. Ensure PostgreSQL is running and accessible
4. Check the troubleshooting section above

For Supabase-specific issues, refer to the [Supabase documentation](https://supabase.com/docs).
