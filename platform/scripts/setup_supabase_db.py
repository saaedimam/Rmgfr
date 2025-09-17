#!/usr/bin/env python3
"""
Supabase Database Setup Script
Sets up the complete database schema for the Anti-Fraud Platform
"""

import os
import asyncio
import asyncpg
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseSetup:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = None
    
    async def connect(self):
        """Connect to Supabase database"""
        try:
            self.connection = await asyncpg.connect(self.db_url)
            logger.info("Connected to Supabase database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from database")
    
    async def execute_sql_file(self, file_path: str) -> bool:
        """Execute SQL file against database"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            await self.connection.execute(sql_content)
            logger.info(f"Executed {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to execute {file_path}: {e}")
            return False
    
    async def setup_database(self):
        """Set up the complete database schema"""
        logger.info("Starting database setup...")
        
        # Get the database directory
        db_dir = Path(__file__).parent.parent / "infra" / "db"
        
        # SQL files in order of execution
        sql_files = [
            "001_core_tables.sql",
            "002_events.sql", 
            "004_rules.sql",
            "005_feature_flags.sql",
            "006_push_tokens.sql",
            "007_incidents_slo.sql",
            "008_audit_timeline.sql",
            "009_pitr.sql",
            "010_pii_policies.sql"
        ]
        
        success_count = 0
        total_files = len(sql_files)
        
        for sql_file in sql_files:
            file_path = db_dir / sql_file
            if file_path.exists():
                if await self.execute_sql_file(str(file_path)):
                    success_count += 1
            else:
                logger.warning(f"SQL file not found: {file_path}")
        
        logger.info(f"Database setup completed: {success_count}/{total_files} files executed successfully")
        return success_count == total_files
    
    async def seed_database(self):
        """Seed database with initial data"""
        logger.info("Seeding database with initial data...")
        
        try:
            # Seed decision matrix
            decision_matrix_file = Path(__file__).parent.parent.parent / "decision_matrix_seed.csv"
            if decision_matrix_file.exists():
                await self._seed_decision_matrix(str(decision_matrix_file))
            
            # Seed segment metrics
            segment_metrics_file = Path(__file__).parent.parent.parent / "segment_metrics_seed.csv"
            if segment_metrics_file.exists():
                await self._seed_segment_metrics(str(segment_metrics_file))
            
            logger.info("Database seeding completed")
            return True
        except Exception as e:
            logger.error(f"Failed to seed database: {e}")
            return False
    
    async def _seed_decision_matrix(self, csv_file: str):
        """Seed decision matrix from CSV"""
        logger.info("Seeding decision matrix...")
        
        # Create decision_matrix table if it doesn't exist
        create_table_sql = """
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
        await self.connection.execute(create_table_sql)
        
        # Read and insert CSV data
        import csv
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                insert_sql = """
                INSERT INTO decision_matrix (event_type, risk_band, customer_segment, action, max_fpr, notes, updated_by, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (event_type, risk_band, customer_segment) 
                DO UPDATE SET 
                    action = EXCLUDED.action,
                    max_fpr = EXCLUDED.max_fpr,
                    notes = EXCLUDED.notes,
                    updated_by = EXCLUDED.updated_by,
                    updated_at = EXCLUDED.updated_at;
                """
                await self.connection.execute(
                    insert_sql,
                    row['event_type'],
                    row['risk_band'],
                    row['customer_segment'],
                    row['action'],
                    float(row['max_fpr']),
                    row.get('notes', ''),
                    row.get('updated_by', 'system'),
                    row.get('updated_at', 'NOW()')
                )
        
        logger.info("Decision matrix seeded successfully")
    
    async def _seed_segment_metrics(self, csv_file: str):
        """Seed segment metrics from CSV"""
        logger.info("Seeding segment metrics...")
        
        # Create segment_metrics table if it doesn't exist
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS segment_metrics (
            id SERIAL PRIMARY KEY,
            segment_name VARCHAR(100) NOT NULL,
            metric_name VARCHAR(100) NOT NULL,
            metric_value DECIMAL(15,4) NOT NULL,
            metric_unit VARCHAR(20),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(segment_name, metric_name)
        );
        """
        await self.connection.execute(create_table_sql)
        
        # Read and insert CSV data
        import csv
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                insert_sql = """
                INSERT INTO segment_metrics (segment_name, metric_name, metric_value, metric_unit, updated_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (segment_name, metric_name) 
                DO UPDATE SET 
                    metric_value = EXCLUDED.metric_value,
                    metric_unit = EXCLUDED.metric_unit,
                    updated_at = EXCLUDED.updated_at;
                """
                await self.connection.execute(
                    insert_sql,
                    row['segment_name'],
                    row['metric_name'],
                    float(row['metric_value']),
                    row.get('metric_unit', ''),
                    'NOW()'
                )
        
        logger.info("Segment metrics seeded successfully")
    
    async def verify_setup(self) -> Dict[str, Any]:
        """Verify database setup by checking table existence and data"""
        logger.info("Verifying database setup...")
        
        verification_results = {
            "tables_created": [],
            "tables_missing": [],
            "data_counts": {},
            "overall_success": True
        }
        
        # List of expected tables
        expected_tables = [
            "organizations", "projects", "api_keys", "profiles", "events",
            "decisions", "cases", "decision_matrix", "segment_metrics",
            "feature_flags", "mobile_push_tokens", "incidents", "audit_events"
        ]
        
        for table in expected_tables:
            try:
                result = await self.connection.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                    table
                )
                if result:
                    verification_results["tables_created"].append(table)
                    
                    # Get row count
                    count = await self.connection.fetchval(f"SELECT COUNT(*) FROM {table}")
                    verification_results["data_counts"][table] = count
                else:
                    verification_results["tables_missing"].append(table)
                    verification_results["overall_success"] = False
            except Exception as e:
                logger.error(f"Error checking table {table}: {e}")
                verification_results["tables_missing"].append(table)
                verification_results["overall_success"] = False
        
        return verification_results

async def main():
    """Main setup function"""
    # Get database URL from environment
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        logger.error("SUPABASE_DB_URL environment variable not set")
        logger.info("Please set SUPABASE_DB_URL to your Supabase database connection string")
        logger.info("Example: export SUPABASE_DB_URL='postgresql://postgres:password@db.project.supabase.co:5432/postgres'")
        return False
    
    setup = SupabaseSetup(db_url)
    
    try:
        # Connect to database
        await setup.connect()
        
        # Set up database schema
        schema_success = await setup.setup_database()
        if not schema_success:
            logger.error("Database schema setup failed")
            return False
        
        # Seed database with initial data
        seed_success = await setup.seed_database()
        if not seed_success:
            logger.warning("Database seeding failed, but schema was created")
        
        # Verify setup
        verification = await setup.verify_setup()
        
        # Print results
        logger.info("=== Database Setup Results ===")
        logger.info(f"Tables created: {len(verification['tables_created'])}")
        logger.info(f"Tables missing: {len(verification['tables_missing'])}")
        logger.info(f"Overall success: {verification['overall_success']}")
        
        if verification['tables_created']:
            logger.info("\nCreated tables:")
            for table in verification['tables_created']:
                count = verification['data_counts'].get(table, 0)
                logger.info(f"  - {table}: {count} rows")
        
        if verification['tables_missing']:
            logger.warning("\nMissing tables:")
            for table in verification['tables_missing']:
                logger.warning(f"  - {table}")
        
        return verification['overall_success']
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        return False
    finally:
        await setup.disconnect()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
