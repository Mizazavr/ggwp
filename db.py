from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

DATABASE_URL = os.environ['DATABASE_URL'].replace('postgresql://', 'postgresql+asyncpg://')
# Remove sslmode parameter if present
if 'sslmode' in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace('?sslmode=require', '')
    
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Enable logging
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
