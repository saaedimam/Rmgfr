#!/usr/bin/env python3
"""
Initialize the database for the API
"""

import asyncio
from src.models.database import engine, Base

async def init_db():
    """Initialize the database tables"""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
