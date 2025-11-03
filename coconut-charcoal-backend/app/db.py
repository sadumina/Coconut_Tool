# app/db.py
from __future__ import annotations
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import settings

_client: Optional[AsyncIOMotorClient] = None

async def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        print("🔌 Creating MongoDB client...")

        # ✅ SRV enabled Atlas connection, TLS required
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,   # ✅ fix for Windows DNS/SSL issues
            serverSelectionTimeoutMS=20000      # ✅ give MongoDB time to resolve DNS
        )

    return _client


async def get_db():
    client = await get_client()
    return client[settings.MONGODB_DB]
