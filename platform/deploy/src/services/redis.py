"""
Redis service for caching and rate limiting
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis


logger = logging.getLogger(__name__)


class RedisService:
    """Async Redis service for caching and rate limiting"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self.redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis disconnected")
    
    async def ping(self) -> bool:
        """
        Ping Redis server
        
        Returns:
            bool: True if successful
        """
        try:
            result = await self.redis.ping()
            return result is True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get value by key
        
        Args:
            key: Redis key
            
        Returns:
            Optional[str]: Value if exists, None otherwise
        """
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET failed for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Union[str, Dict, List], 
        expire: Optional[int] = None
    ) -> bool:
        """
        Set value by key
        
        Args:
            key: Redis key
            value: Value to store
            expire: Expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                await self.redis.setex(key, expire, value)
            else:
                await self.redis.set(key, value)
            
            return True
        except Exception as e:
            logger.error(f"Redis SET failed for key {key}: {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """
        Delete keys
        
        Args:
            *keys: Keys to delete
            
        Returns:
            int: Number of keys deleted
        """
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE failed for keys {keys}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists
        
        Args:
            key: Redis key
            
        Returns:
            bool: True if key exists
        """
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS failed for key {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration for key
        
        Args:
            key: Redis key
            seconds: Expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE failed for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment numeric value
        
        Args:
            key: Redis key
            amount: Amount to increment by
            
        Returns:
            int: New value after increment
        """
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCRBY failed for key {key}: {e}")
            return 0
    
    async def get_json(self, key: str) -> Optional[Union[Dict, List]]:
        """
        Get JSON value by key
        
        Args:
            key: Redis key
            
        Returns:
            Optional[Union[Dict, List]]: Parsed JSON value
        """
        try:
            value = await self.get(key)
            if value:
                return json.loads(value)
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode failed for key {key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Redis GET JSON failed for key {key}: {e}")
            return None
    
    async def set_json(
        self, 
        key: str, 
        value: Union[Dict, List], 
        expire: Optional[int] = None
    ) -> bool:
        """
        Set JSON value by key
        
        Args:
            key: Redis key
            value: JSON-serializable value
            expire: Expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, expire)
        except Exception as e:
            logger.error(f"Redis SET JSON failed for key {key}: {e}")
            return False
    
    async def health_check(self) -> bool:
        """
        Check Redis health
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            return await self.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
