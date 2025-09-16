"""
Database service for async PostgreSQL operations
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import asyncpg
from asyncpg import Pool, Connection


logger = logging.getLogger(__name__)


class DatabaseService:
    """Async PostgreSQL database service"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[Pool] = None
    
    async def connect(self) -> None:
        """Connect to the database and create connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'jit': 'off',  # Disable JIT for better performance in some cases
                }
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def execute(self, query: str, params: List[Any] = None) -> str:
        """
        Execute a query that doesn't return data
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            str: Query result status
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *(params or []))
    
    async def fetch_one(self, query: str, params: List[Any] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Optional[Dict]: Single row as dictionary, or None if not found
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *(params or []))
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """
        Fetch all rows
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List[Dict]: List of rows as dictionaries
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *(params or []))
            return [dict(row) for row in rows]
    
    async def execute_query(self, query: str, params: List[Any] = None) -> Any:
        """
        Execute a query and return the result
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Any: Query result
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *(params or []))
    
    async def transaction(self):
        """
        Get a database transaction context manager
        
        Returns:
            Transaction context manager
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        return self.pool.acquire()
    
    async def health_check(self) -> bool:
        """
        Check database health
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            await self.execute_query("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
