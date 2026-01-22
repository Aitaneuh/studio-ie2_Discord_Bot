import httpx
import asyncio
from config import API_TOKEN

async def get_player_data(tag):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    # encoding # to %23
    clean_tag = tag.replace("#", "%23")
    url = f"https://api.clashroyale.com/v1/players/{clean_tag}"
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "name": data['name'],
                "trophies": data['trophies'],
                "best": data['bestTrophies'],
                "acc_wins": data['wins']
            }
        return None
