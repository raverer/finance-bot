import httpx
from rapidfuzz import process, fuzz

MFAPI_LIST_URL = "https://api.mfapi.in/mf"

async def get_all_schemes():
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(MFAPI_LIST_URL)
        resp.raise_for_status()
        return resp.json()

async def find_scheme_code_by_name(name_query: str):
    schemes = await get_all_schemes()

    # Extract list of names for fuzzy matching
    names = [s["schemeName"] for s in schemes]

    match, score, index = process.extractOne(
        name_query, 
        names, 
        scorer=fuzz.WRatio
    )

    # Best fuzzy match
    best_scheme = schemes[index]

    return {
        "scheme_code": best_scheme["schemeCode"],
        "scheme_name": best_scheme["schemeName"]
    }
