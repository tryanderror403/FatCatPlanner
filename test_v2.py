import asyncio
import logging
from xivapi_sync import sync_content_from_xivapi

logging.basicConfig(level=logging.INFO)

async def test():
    try:
        await sync_content_from_xivapi()
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(test())
