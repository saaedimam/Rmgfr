#!/usr/bin/env python3
"""
Seed the database with sample data
"""

import asyncio
from src.models.database import async_session_maker, Organization, Project, APIKey

async def seed_db():
    """Seed the database with sample data"""
    print("Seeding database with sample data...")

    async with async_session_maker() as session:
        # Create organization
        org = Organization(
            name="Demo Organization",
            slug="demo-org",
            settings={"timezone": "UTC", "currency": "USD"}
        )
        session.add(org)
        await session.flush()

        # Create project
        project = Project(
            organization_id=org.id,
            name="Demo Project",
            slug="demo-project",
            settings={"risk_threshold": 0.7, "auto_approve_threshold": 0.3}
        )
        session.add(project)
        await session.flush()

        # Create API key
        api_key = APIKey(
            project_id=project.id,
            name="Demo API Key",
            key_hash="demo-key-hash",
            permissions=["read", "write", "admin"]
        )
        session.add(api_key)

        await session.commit()

        print(f"✅ Sample data created successfully!")
        print(f"📋 Project ID: {project.id}")
        print(f"🔑 API Key: demo-key")

if __name__ == "__main__":
    asyncio.run(seed_db())
