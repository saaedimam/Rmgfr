"""
Database Service for Supabase Integration
Handles database connections and operations
"""

import os
import asyncio
import asyncpg
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for Supabase PostgreSQL"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.db_url = os.getenv('SUPABASE_DB_URL')
        
        if not self.db_url:
            logger.warning("SUPABASE_DB_URL not set, database operations will fail")
    
    async def initialize(self, min_connections: int = 5, max_connections: int = 20):
        """Initialize database connection pool"""
        if not self.db_url:
            raise ValueError("SUPABASE_DB_URL environment variable not set")
        
        try:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=min_connections,
                max_size=max_connections,
                command_timeout=60
            )
            logger.info(f"Database pool initialized with {min_connections}-{max_connections} connections")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def execute_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return single result"""
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def execute_command(self, command: str, *args) -> str:
        """Execute a command (INSERT, UPDATE, DELETE) and return status"""
        async with self.get_connection() as conn:
            result = await conn.execute(command, *args)
            return result
    
    async def execute_transaction(self, operations: List[tuple]) -> bool:
        """Execute multiple operations in a transaction"""
        async with self.get_connection() as conn:
            async with conn.transaction():
                try:
                    for operation in operations:
                        query, args = operation
                        await conn.execute(query, *args)
                    return True
                except Exception as e:
                    logger.error(f"Transaction failed: {e}")
                    raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            async with self.get_connection() as conn:
                # Test basic connectivity
                result = await conn.fetchval("SELECT 1")
                
                # Get database info
                db_name = await conn.fetchval("SELECT current_database()")
                db_version = await conn.fetchval("SELECT version()")
                
                # Get connection count
                active_connections = await conn.fetchval(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                )
                
                return {
                    "status": "healthy",
                    "database": db_name,
                    "version": db_version.split()[0] if db_version else "unknown",
                    "active_connections": active_connections,
                    "pool_size": self.pool.get_size() if self.pool else 0,
                    "pool_idle": self.pool.get_idle_size() if self.pool else 0
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global database service instance
db_service = DatabaseService()

# Dependency for FastAPI
async def get_database():
    """FastAPI dependency for database service"""
    return db_service

# Database initialization function
async def init_database():
    """Initialize database service"""
    await db_service.initialize()

# Database cleanup function
async def close_database():
    """Close database service"""
    await db_service.close()