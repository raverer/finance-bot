import httpx
from datetime import datetime
from math import pow
from ..schemas import SIPInput, SIPResult

MFAPI_BASE = "https://api.mfapi.in"


# --------------------------------------------------
# Fetch full scheme data (metadata + NAV history)
# --------------------------------------------------
async def fetch_scheme_full(scheme_code: str):
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{MFAPI_BASE}/mf/{scheme_code}")
        resp.raise_for_status()
        return resp.json()


# --------------------------------------------------
# Simple SIP calculation (formula-based)
# --------------------------------------------------
def calculate_sip_formula(monthly_amount: float, years: float, expected_return: float):
    """
    FV = P × [ ((1+r)^n - 1) × (1+r) ] / r
    r = monthly interest rate
    n = total months
    """
    n = int(years * 12)
    r = expected_return / 12 / 100

    if r == 0:
        fv = monthly_amount * n
        return (monthly_amount * n), fv

    fv = monthly_amount * (((pow(1 + r, n) - 1) * (1 + r)) / r)
    invested = monthly_amount * n
    return invested, fv


# --------------------------------------------------
# NAV-based SIP calculation (real market simulation)
# --------------------------------------------------
async def calculate_sip_nav_based(payload: SIPInput) -> SIPResult:
    scheme_data = await fetch_scheme_full(payload.scheme_code)

    meta = scheme_data.get("meta", {})
    nav_history = scheme_data.get("data", [])

    if not nav_history:
        raise ValueError("No NAV history available for this scheme.")

    # Extract metadata
    scheme_name = meta.get("scheme_name", "Unknown Fund")
    scheme_category = meta.get("scheme_category", "Unknown Category")
    scheme_type = meta.get("scheme_type", "Unknown Type")

    # NAV history: reverse to oldest → newest
    nav_history.reverse()

    monthly_amount = payload.monthly_amount
    invest_months = int(payload.years * 12)
    sip_day = payload.sip_day

    total_units = 0.0
    total_invested = 0.0

    month_counter = 0
    latest_nav = float(nav_history[-1]["nav"])

    for entry in nav_history:
        if month_counter >= invest_months:
            break

        date_str = entry["date"]  # e.g. "01-01-2025"
        nav_date = datetime.strptime(date_str, "%d-%m-%Y")

        # Buy only on SIP day
        if nav_date.day != sip_day:
            continue

        nav_value = float(entry["nav"])
        units = monthly_amount / nav_value

        total_units += units
        total_invested += monthly_amount
        month_counter += 1

    current_value = total_units * latest_nav
    profit = current_value - total_invested

    absolute_return = (profit / total_invested * 100) if total_invested else 0

    annual_return = (
        (pow((current_value / total_invested), (1 / payload.years)) - 1) * 100
        if total_invested > 0 and payload.years > 0
        else 0
    )

    return SIPResult(
        scheme_name=scheme_name,
        scheme_category=scheme_category,
        scheme_type=scheme_type,
        total_invested=round(total_invested, 2),
        current_value=round(current_value, 2),
        profit=round(profit, 2),
        absolute_return_percent=round(absolute_return, 2),
        annual_return_percent=round(annual_return, 2),
        total_units=round(total_units, 4),
        latest_nav=round(latest_nav, 2),
    )
