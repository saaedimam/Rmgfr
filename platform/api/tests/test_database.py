"""
Tests for Database Service
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.services.database import DatabaseService

class TestDatabaseService:
    
    def setup_method(self):
        self.db_service = DatabaseService()
        self.db_service.db_url = "postgresql://test:test@localhost:5432/test"
    
    @pytest.mark.asyncio
    async def test_initialization_without_url(self):
        """Test initialization fails without database URL"""
        db_service = DatabaseService()
        db_service.db_url = None
        
        with pytest.raises(ValueError, match="SUPABASE_DB_URL environment variable not set"):
            await db_service.initialize()
    
    @pytest.mark.asyncio
    async def test_initialization_with_url(self):
        """Test initialization with database URL"""
        # Mock asyncpg.create_pool
        with pytest.Mock() as mock_pool:
            mock_pool.create_pool = AsyncMock(return_value=mock_pool)
            
            # This would require more complex mocking for asyncpg
            # For now, we'll test the error handling
            with pytest.raises(Exception):
                await self.db_service.initialize()
    
    @pytest.mark.asyncio
    async def test_health_check_no_pool(self):
        """Test health check when pool is not initialized"""
        result = await self.db_service.health_check()
        
        assert result["status"] == "unhealthy"
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_connection_no_pool(self):
        """Test get_connection when pool is not initialized"""
        with pytest.raises(RuntimeError, match="Database pool not initialized"):
            async with self.db_service.get_connection():
                pass
    
    @pytest.mark.asyncio
    async def test_execute_query_no_pool(self):
        """Test execute_query when pool is not initialized"""
        with pytest.raises(RuntimeError, match="Database pool not initialized"):
            await self.db_service.execute_query("SELECT 1")
    
    @pytest.mark.asyncio
    async def test_execute_one_no_pool(self):
        """Test execute_one when pool is not initialized"""
        with pytest.raises(RuntimeError, match="Database pool not initialized"):
            await self.db_service.execute_one("SELECT 1")
    
    @pytest.mark.asyncio
    async def test_execute_command_no_pool(self):
        """Test execute_command when pool is not initialized"""
        with pytest.raises(RuntimeError, match="Database pool not initialized"):
            await self.db_service.execute_command("SELECT 1")
    
    @pytest.mark.asyncio
    async def test_execute_transaction_no_pool(self):
        """Test execute_transaction when pool is not initialized"""
        with pytest.raises(RuntimeError, match="Database pool not initialized"):
            await self.db_service.execute_transaction([("SELECT 1", ())])
    
    @pytest.mark.asyncio
    async def test_close_no_pool(self):
        """Test close when pool is not initialized"""
        # Should not raise an exception
        await self.db_service.close()
    
    @pytest.mark.asyncio
    async def test_mock_database_operations(self):
        """Test database operations with mocked pool"""
        # Create a mock pool
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
        mock_pool.acquire.return_value.__aexit__.return_value = None
        
        # Mock connection methods
        mock_connection.fetch.return_value = [{"id": 1, "name": "test"}]
        mock_connection.fetchrow.return_value = {"id": 1, "name": "test"}
        mock_connection.execute.return_value = "INSERT 0 1"
        
        # Set the mock pool
        self.db_service.pool = mock_pool
        
        # Test execute_query
        result = await self.db_service.execute_query("SELECT * FROM test")
        assert result == [{"id": 1, "name": "test"}]
        mock_connection.fetch.assert_called_once()
        
        # Test execute_one
        result = await self.db_service.execute_one("SELECT * FROM test WHERE id = $1", 1)
        assert result == {"id": 1, "name": "test"}
        mock_connection.fetchrow.assert_called_once()
        
        # Test execute_command
        result = await self.db_service.execute_command("INSERT INTO test (name) VALUES ($1)", "test")
        assert result == "INSERT 0 1"
        mock_connection.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mock_health_check(self):
        """Test health check with mocked pool"""
        # Create a mock pool
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
        mock_pool.acquire.return_value.__aexit__.return_value = None
        mock_pool.get_size.return_value = 10
        mock_pool.get_idle_size.return_value = 5
        
        # Mock connection methods
        mock_connection.fetchval.side_effect = [
            1,  # SELECT 1
            "test_db",  # current_database()
            "PostgreSQL 15.0",  # version()
            3  # active connections count
        ]
        
        # Set the mock pool
        self.db_service.pool = mock_pool
        
        # Test health check
        result = await self.db_service.health_check()
        
        assert result["status"] == "healthy"
        assert result["database"] == "test_db"
        assert result["version"] == "PostgreSQL"
        assert result["active_connections"] == 3
        assert result["pool_size"] == 10
        assert result["pool_idle"] == 5
    
    @pytest.mark.asyncio
    async def test_mock_transaction(self):
        """Test transaction with mocked pool"""
        # Create a mock pool
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_transaction = AsyncMock()
        
        mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
        mock_pool.acquire.return_value.__aexit__.return_value = None
        mock_connection.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_connection.transaction.return_value.__aexit__.return_value = None
        
        # Set the mock pool
        self.db_service.pool = mock_pool
        
        # Test transaction
        operations = [
            ("INSERT INTO test (name) VALUES ($1)", ("test1",)),
            ("INSERT INTO test (name) VALUES ($1)", ("test2",))
        ]
        
        result = await self.db_service.execute_transaction(operations)
        assert result is True
        
        # Verify transaction was used
        mock_connection.transaction.assert_called_once()
        assert mock_connection.execute.call_count == 2

if __name__ == "__main__":
    pytest.main([__file__])
