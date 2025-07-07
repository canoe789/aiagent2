#!/usr/bin/env python3
"""Test database connection"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from dotenv import load_dotenv
load_dotenv()

from database.connection import db_manager

async def test_db():
    try:
        print("Connecting to database...")
        await db_manager.connect()
        print("✅ Database connected successfully")
        
        # Test query
        result = await db_manager.fetch_one("SELECT version()")
        print(f"Database version: {result}")
        
        await db_manager.disconnect()
        print("✅ Database disconnected")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())