import asyncio
import aiohttp
import json

async def test():
    url = "https://v2.xivapi.com/api/sheet/ContentFinderCondition?limit=2"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(f"Status: {resp.status}")
            data = await resp.json()
            print(json.dumps(data, indent=2))

asyncio.run(test())
