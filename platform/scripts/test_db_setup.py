#!/usr/bin/env python3
"""
Test Database Setup Script
Creates a local test database for development
"""

import os
import asyncio
import asyncpg
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_test_database():
    """Create a test database for development"""
    
    # Test database configuration
    test_db_config = {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "password",
        "database": "antifraud_test"
    }
    
    # Create connection string
    db_url = f"postgresql://{test_db_config['user']}:{test_db_config['password']}@{test_db_config['host']}:{test_db_config['port']}/postgres"
    
    try:
        # Connect to PostgreSQL server (not specific database)
        conn = await asyncpg.connect(db_url)
        
        # Check if test database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            test_db_config['database']
        )
        
        if not exists:
            # Create test database
            await conn.execute(f"CREATE DATABASE {test_db_config['database']}")
            logger.info(f"Created test database: {test_db_config['database']}")
        else:
            logger.info(f"Test database already exists: {test_db_config['database']}")
        
        await conn.close()
        
        # Now connect to the test database and create tables
        test_db_url = f"postgresql://{test_db_config['user']}:{test_db_config['password']}@{test_db_config['host']}:{test_db_config['port']}/{test_db_config['database']}"
        
        conn = await asyncpg.connect(test_db_url)
        
        # Create basic tables
        tables_sql = """
        -- Organizations table
        CREATE TABLE IF NOT EXISTS organizations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(100) UNIQUE NOT NULL,
            settings JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Projects table
        CREATE TABLE IF NOT EXISTS projects (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(100) NOT NULL,
            settings JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(organization_id, slug)
        );

        -- API Keys table
        CREATE TABLE IF NOT EXISTS api_keys (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            key_hash VARCHAR(255) UNIQUE NOT NULL,
            permissions JSONB DEFAULT '[]',
            last_used_at TIMESTAMP WITH TIME ZONE,
            expires_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Events table
        CREATE TABLE IF NOT EXISTS events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            event_type VARCHAR(50) NOT NULL,
            event_data JSONB DEFAULT '{}',
            profile_id VARCHAR(255),
            session_id VARCHAR(255),
            device_fingerprint VARCHAR(255),
            ip_address INET,
            user_agent TEXT,
            event_ts TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Decisions table
        CREATE TABLE IF NOT EXISTS decisions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            event_id UUID REFERENCES events(id) ON DELETE CASCADE,
            profile_id UUID,
            decision VARCHAR(20) NOT NULL,
            risk_score DECIMAL(3,2),
            reasons TEXT[],
            rules_fired TEXT[],
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Cases table
        CREATE TABLE IF NOT EXISTS cases (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            decision_id UUID NOT NULL REFERENCES decisions(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'open',
            assigned_to VARCHAR(255),
            resolution VARCHAR(20),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Decision matrix table
        CREATE TABLE IF NOT EXISTS decision_matrix (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            risk_band VARCHAR(20) NOT NULL,
            customer_segment VARCHAR(50) NOT NULL,
            action VARCHAR(20) NOT NULL,
            max_fpr DECIMAL(5,4) NOT NULL,
            notes TEXT,
            updated_by VARCHAR(255),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(event_type, risk_band, customer_segment)
        );
        """
        
        await conn.execute(tables_sql)
        logger.info("Created test database tables")
        
        # Insert sample data
        sample_data_sql = """
        -- Insert sample organization
        INSERT INTO organizations (id, name, slug) VALUES 
        ('550e8400-e29b-41d4-a716-446655440000', 'Test Organization', 'test-org')
        ON CONFLICT (slug) DO NOTHING;

        -- Insert sample project
        INSERT INTO projects (id, organization_id, name, slug) VALUES 
        ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'Test Project', 'test-project')
        ON CONFLICT (organization_id, slug) DO NOTHING;

        -- Insert sample API key
        INSERT INTO api_keys (project_id, name, key_hash) VALUES 
        ('550e8400-e29b-41d4-a716-446655440001', 'test-key', 'test-hash-123')
        ON CONFLICT (key_hash) DO NOTHING;

        -- Insert sample decision matrix
        INSERT INTO decision_matrix (event_type, risk_band, customer_segment, action, max_fpr, notes, updated_by) VALUES 
        ('login', 'low', 'returning', 'allow', 0.01, 'Low risk returning users', 'system'),
        ('login', 'high', 'new_user', 'review', 0.005, 'High risk new users need review', 'system'),
        ('payment', 'critical', 'any', 'deny', 0.002, 'Critical risk payments denied', 'system')
        ON CONFLICT (event_type, risk_band, customer_segment) DO NOTHING;
        """
        
        await conn.execute(sample_data_sql)
        logger.info("Inserted sample data")
        
        await conn.close()
        
        # Print connection info
        logger.info("=== Test Database Setup Complete ===")
        logger.info(f"Database: {test_db_config['database']}")
        logger.info(f"Host: {test_db_config['host']}:{test_db_config['port']}")
        logger.info(f"User: {test_db_config['user']}")
        logger.info(f"Connection URL: {test_db_url}")
        logger.info("")
        logger.info("To use this database, set:")
        logger.info(f"export SUPABASE_DB_URL='{test_db_url}'")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create test database: {e}")
        logger.info("Make sure PostgreSQL is running and accessible")
        logger.info("Default connection: postgresql://postgres:password@localhost:5432/postgres")
        return False

async def main():
    """Main setup function"""
    success = await create_test_database()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
