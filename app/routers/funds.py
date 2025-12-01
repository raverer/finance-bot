from fastapi import APIRouter, HTTPException
from ..services.mfapi import get_scheme_data

router = APIRouter(prefix="/funds", tags=["Mutual Funds"])


@router.get("/{scheme_code}")
async def get_fund(scheme_code: str):
    """
    Proxies data from https://www.mfapi.in/
    """
    try:
        data = await get_scheme_data(scheme_code)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error fetching scheme data: {e}")
