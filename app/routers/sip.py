from fastapi import APIRouter, HTTPException
from math import pow

from ..schemas import SIPInput, SIPResult
from ..services.sip import calculate_sip_formula, calculate_sip_nav_based
from ..services.scheme_lookup import find_scheme_code_by_name


router = APIRouter(prefix="/sip", tags=["SIP"])


@router.post("/calculate", response_model=SIPResult)
async def calculate_sip(payload: SIPInput):
    """
    Universal SIP endpoint that handles:
    - NAV-based SIP (real SIP simulation)
    - Formula-based SIP (simple SIP)
    - Scheme name → scheme code lookup (fuzzy)
    """

    # ---------------------------------------------------------
    # 1️⃣ User provides scheme_name only → Get scheme_code
    # ---------------------------------------------------------
    if payload.scheme_name and not payload.scheme_code:
        try:
            match = await find_scheme_code_by_name(payload.scheme_name)
            payload.scheme_code = match["scheme_code"]
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Could not match scheme name. Error: {str(e)}"
            )

    # ---------------------------------------------------------
    # 2️⃣ Validate scheme_code
    # ---------------------------------------------------------
    if not payload.scheme_code:
        raise HTTPException(
            status_code=400,
            detail="Please provide either scheme_name or scheme_code."
        )

    # ---------------------------------------------------------
    # 3️⃣ NAV-BASED SIP (accurate mode)
    # ---------------------------------------------------------
    try:
        if payload.use_nav_history:
            return await calculate_sip_nav_based(payload)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"NAV-based SIP failed: {str(e)}"
        )

    # ---------------------------------------------------------
    # 4️⃣ Formula-based SIP (simple mode)
    # ---------------------------------------------------------
    try:
        invested, value = calculate_sip_formula(
            payload.monthly_amount,
            payload.years,
            payload.expected_return
        )

        profit = value - invested
        absolute_return = (profit / invested * 100) if invested else 0

        annual_return = (
            (pow((value / invested), (1 / payload.years)) - 1) * 100
            if invested > 0 and payload.years > 0
            else 0
        )

        # Placeholders since formula mode doesn’t use NAV or real units
        return SIPResult(
            scheme_name="N/A (Formula Mode — no NAV used)",
            scheme_category="N/A",
            scheme_type="N/A",
            total_invested=round(invested, 2),
            current_value=round(value, 2),
            profit=round(profit, 2),
            absolute_return_percent=round(absolute_return, 2),
            annual_return_percent=round(annual_return, 2),
            total_units=0.0,
            latest_nav=0.0
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Formula-based SIP failed: {str(e)}"
        )
