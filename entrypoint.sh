#!/bin/sh
set -e

echo "Initializing database tables..."
python -c "
import asyncio
from app.database import Base, engine
import app.models

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Database tables successfully initialized!')

asyncio.run(init_db())
"

exec "$@"
