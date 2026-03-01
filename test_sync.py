import asyncio
from xivapi_sync import sync_content_from_xivapi
import db

async def main():
    await db.init_db()
    count = await sync_content_from_xivapi()
    print(f"Synced {count} records")

if __name__ == "__main__":
    asyncio.run(main())
