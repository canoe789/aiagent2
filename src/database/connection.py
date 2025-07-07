"""
Database connection management for Project HELIX v2.0
"""

import asyncio
import asyncpg
import os
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

class DatabaseManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.connection_url = self._build_connection_url()
    
    def _build_connection_url(self) -> str:
        """Build PostgreSQL connection URL from environment variables"""
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        database = os.getenv('POSTGRES_DB', 'helix')
        user = os.getenv('POSTGRES_USER', 'helix_user')
        password = os.getenv('POSTGRES_PASSWORD', 'helix_password')
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    async def connect(self, min_size: int = 5, max_size: int = 20) -> None:
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_url,
                min_size=min_size,
                max_size=max_size,
                command_timeout=60
            )
            logger.info("Database connection pool created", 
                       min_size=min_size, max_size=max_size)
        except Exception as e:
            logger.error("Failed to create database connection pool", error=str(e))
            raise
    
    async def disconnect(self) -> None:
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query that doesn't return rows"""
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch_one(self, query: str, *args) -> Optional[dict]:
        """Fetch a single row"""
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, *args) -> list[dict]:
        """Fetch multiple rows"""
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def transaction(self):
        """Get a database transaction context"""
        connection = await self.pool.acquire()
        transaction = connection.transaction()
        return TransactionContext(connection, transaction, self.pool)

class TransactionContext:
    """Context manager for database transactions"""
    
    def __init__(self, connection, transaction, pool):
        self.connection = connection
        self.transaction = transaction
        self.pool = pool
    
    async def __aenter__(self):
        await self.transaction.start()
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.transaction.rollback()
        else:
            await self.transaction.commit()
        await self.pool.release(self.connection)

# Global database manager instance
db_manager = DatabaseManager()

async def get_db_connection():
    """Get database connection (for dependency injection)"""
    if not db_manager.pool:
        await db_manager.connect()
    return db_manager