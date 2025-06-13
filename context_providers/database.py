from typing import Dict, Any
from .base import BaseContextProvider
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import aiosqlite

class DatabaseContextProvider(BaseContextProvider):
    def __init__(self, connection_string: str = "sqlite+aiosqlite:///mcp.db"):
        self.connection_string = connection_string
        self.engine = None
        self.async_session = None

    async def initialize(self):
        """Initialize the database connection"""
        self.engine = create_async_engine(
            self.connection_string,
            echo=False,
            future=True
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_context(self, query: str, **kwargs) -> Dict[str, Any]:
        """Get context from the database"""
        if not self.engine:
            await self.initialize()

        required_fields = kwargs.get('required_fields', [])
        
        async with self.async_session() as session:
            # Example implementation - modify based on your needs
            # This is a simple search implementation
            search_query = text("""
                SELECT * FROM your_table 
                WHERE your_column LIKE :search_term
                LIMIT 10
            """)
            
            result = await session.execute(
                search_query,
                {"search_term": f"%{query}%"}
            )
            
            rows = result.fetchall()
            
            return {
                "data": [dict(row) for row in rows],
                "source": "database",
                "query": query,
                "fields": required_fields
            }

    async def validate_connection(self) -> bool:
        """Validate the database connection"""
        try:
            if not self.engine:
                await self.initialize()
            
            async with self.async_session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    async def close(self):
        """Close the database connection"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.async_session = None 