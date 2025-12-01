import httpx


BASE_URL = "https://api.mfapi.in"


async def get_scheme_data(scheme_code: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{BASE_URL}/mf/{scheme_code}")
        resp.raise_for_status()
        return resp.json()
