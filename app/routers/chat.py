# app/routers/chat.py
from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse
import json
import os
import requests
from typing import Optional

# ============================================================
#   USE GROQ (cloud) – OLLAMA CANNOT RUN ON RAILWAY
# ============================================================
USE_OLLAMA = False   # IMPORTANT: keep this False on Railway

if USE_OLLAMA:
    from ..services.llm_ollama import call_llm_ollama as call_llm
else:
    from ..services.llm_groq import call_llm_groq as call_llm

router = APIRouter(prefix="/chat", tags=["Chat / LLM"])

# Internal base URL to call our own APIs (EMI, SIP, funds) from inside the backend
INTERNAL_BASE = os.getenv("INTERNAL_BASE_URL", "http://127.0.0.1:8000")

# Public MF API (change if mfapi provides a different search endpoint)
# NOTE: If mfapi search endpoint is different, update MF_SEARCH_URL accordingly
MF_SEARCH_URL = "https://api.mfapi.in/mf/search?q="     # attempt — adjust if needed
MF_BY_CODE_URL = "https://api.mfapi.in/mf/"             # append scheme code


# ============================================================
#  SYSTEM PROMPTS (force English)
# ============================================================
def base_assistant_prompt() -> str:
    return (
        "You are NiveshBuddy, a helpful Indian personal finance assistant. "
        "You simplify EMIs, SIPs, budgeting, and investments in simple, plain ENGLISH. "
        "You are NOT a SEBI-registered advisor; avoid giving specific stock recommendations. "
        "When you produce suggestions for mutual funds, if numeric data (NAV, returns) is available, "
        "use it, but always include a small friendly explanation and a short risk note. "
        "Respond only in English."
    )


def intent_extraction_prompt() -> str:
    return (
        "You are a natural-language financial intent extractor. "
        "You read ANY user message and convert it into structured JSON.\n\n"

        "Your tasks:\n"
        "1. Detect intent (emi, sip, mf, or general).\n"
        "2. Extract numbers from natural language.\n"
        "3. Extract mutual fund names if mentioned.\n"
        "4. Output STRICT JSON ONLY.\n\n"

        "Supported intents:\n"
        "- emi: loan EMI calculation, loan details, interest, tenure\n"
        "- sip: monthly investment, compounding, future value\n"
        "- mf: mutual fund advice, scheme questions, fund suggestions\n"
        "- general: everything else\n\n"

        "You MUST output JSON in this structure:\n"
        "{\n"
        '  \"intent\": \"emi\" | \"sip\" | \"mf\" | \"general\",\n'
        '  \"loan_amount\": float or null,\n'
        '  \"interest_rate\": float or null,\n'
        '  \"tenure_years\": float or null,\n'
        '  \"monthly_amount\": float or null,\n'
        '  \"years\": float or null,\n'
        '  \"expected_return\": float or null,\n'
        '  \"scheme_name\": string or null,\n'
        '  \"income\": float or null\n'
        "}\n\n"

        "Examples of what users may ask:\n"
        "- \"How much EMI for 10 lakh at 8% for 10 years?\" → intent=emi\n"
        "- \"I want to invest 5000 per month for 10 years\" → intent=sip\n"
        "- \"Recommend SIPs for 50k income\" → intent=mf\n"
        "- \"Tell me about Axis Bluechip fund\" → intent=mf\n\n"

        "Rules:\n"
        "- ALWAYS return English output only.\n"
        "- If unsure about a number, put null.\n"
        "- Mutual fund names MUST be copied exactly as user wrote.\n"
        "- DO NOT include explanation, ONLY JSON.\n"
    )



# ============================================================
#  HELPERS
# ============================================================

def safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def call_emi_api(parsed: dict) -> Optional[dict]:
    loan_amount = safe_float(parsed.get("loan_amount"))
    interest_rate = safe_float(parsed.get("interest_rate"))
    tenure_years = safe_float(parsed.get("tenure_years"))

    if loan_amount is None or interest_rate is None or tenure_years is None:
        return None  # not enough inputs

    payload = {
        "loan_amount": loan_amount,
        "annual_interest_rate": interest_rate,
        "tenure_years": tenure_years,
    }

    try:
        res = requests.post(f"{INTERNAL_BASE}/emi/calculate", json=payload, timeout=15)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("EMI API error:", e)
        return None


def call_sip_api(parsed: dict) -> Optional[dict]:
    monthly_amount = safe_float(parsed.get("monthly_amount"))
    years = safe_float(parsed.get("years"))
    expected_return = safe_float(parsed.get("expected_return"))
    scheme_name = parsed.get("scheme_name")

    if monthly_amount is None or years is None:
        return None  # not enough inputs

    payload = {
        "scheme_code": None,
        "scheme_name": scheme_name,
        "monthly_amount": monthly_amount,
        "years": years,
        "sip_day": 5,
        "expected_return": expected_return if expected_return is not None else 12.0,
        "use_nav_history": True,
    }

    try:
        res = requests.post(f"{INTERNAL_BASE}/sip/calculate", json=payload, timeout=25)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("SIP API error:", e)
        return None


# ---------- Mutual Fund helpers (mfapi) ----------
def mf_search_scheme(scheme_name: str) -> Optional[dict]:
    """
    Try to find scheme(s) by name from mfapi. Returns first match meta or None.
    Note: public mfapi endpoints can vary. Adjust MF_SEARCH_URL if the provider uses different query params.
    """
    if not scheme_name:
        return None
    try:
        url = MF_SEARCH_URL + requests.utils.quote(scheme_name)
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print("MF search not 200:", r.status_code, r.text)
            return None
        data = r.json()
        # many implementations return 'data' list or a top-level array - try to handle both
        if isinstance(data, list) and len(data) > 0:
            return data[0]  # return first match
        if isinstance(data, dict):
            # some search endpoints return {'data': [...]} or {'meta': ...}
            if "data" in data and isinstance(data["data"], list) and data["data"]:
                return data["data"][0]
            if "meta" in data:
                return data["meta"]
        return None
    except Exception as e:
        print("MF search error:", e)
        return None


def mf_get_nav_by_code(scheme_code: str) -> Optional[dict]:
    """
    Fetch NAV history or current NAV by scheme code (mfapi 'mf/{code}' style).
    """
    try:
        url = MF_BY_CODE_URL + str(scheme_code)
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print("MF by code not 200:", r.status_code, r.text)
            return None
        return r.json()
    except Exception as e:
        print("MF NAV fetch error:", e)
        return None


def recommend_mfs_by_income(income: float, top_n: int = 5) -> Optional[dict]:
    """
    Simple heuristic to pick allocation buckets based on income.
    This function doesn't pick exact scheme codes (those change).
    Instead, we:
     - Ask LLM to return a short list of recommended fund types and (optionally) example schemes
       and prefer real-time MF data if mfapi returns scheme info.
    We'll call the LLM with the fetched NAV data (if available) to craft user-facing suggestions.
    """
    # Basic allocation logic
    if income is None:
        income = 0.0

    if income < 30000:
        profile = "conservative"
        monthly_sip_budget = income * 0.10
    elif income < 100000:
        profile = "moderate"
        monthly_sip_budget = income * 0.15
    else:
        profile = "growth"
        monthly_sip_budget = income * 0.20

    # Create a prompt for the LLM: ask for fund types and examples; we will try to enrich with MF API data if possible
    prompt = (
        base_assistant_prompt()
        + f"\nUser income: {income:.2f}. Investment profile: {profile}. "
          f"Suggest a short SIP allocation for monthly SIP = {monthly_sip_budget:.2f}. "
          "Return suggestions in English. For each suggested fund type, if you can find live fund NAV data "
          "or a recent fund name from mfapi, include the scheme name and a one-line reason. Keep total suggestions "
          f"to {top_n} items."
    )

    # Let LLM produce a primary suggestion; it will be refined if we can fetch MF data
    llm_primary = call_llm([{"role": "system", "content": prompt}, {"role": "user", "content": "Provide recommendations."}])

    return {
        "profile": profile,
        "monthly_sip_budget": monthly_sip_budget,
        "llm_recommendation": llm_primary,
    }


# ============================================================
#  Parsing helper using LLM
# ============================================================
def run_intent_extraction(user_message: str) -> dict:
    system_prompt = intent_extraction_prompt()
    llm_response = call_llm([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ])

    try:
        parsed = json.loads(llm_response)
        if "intent" not in parsed:
            raise ValueError("Missing 'intent' in parsed JSON")
        return parsed
    except Exception as e:
        print("Intent parse error:", e, "LLM said:", llm_response)
        return {
            "intent": "general",
            "loan_amount": None,
            "interest_rate": None,
            "tenure_years": None,
            "monthly_amount": None,
            "years": None,
            "expected_return": None,
            "scheme_name": None,
            "income": None,
        }


# ============================================================
#  MAIN CHAT ENDPOINT
# ============================================================
@router.post("/", response_model=ChatResponse)
def chat_with_assistant(payload: ChatRequest):
    user_msg = payload.message

    try:
        # 1) Detect intent + extract params
        parsed = run_intent_extraction(user_msg)
        intent = parsed.get("intent", "general")

        # EMI flow
        if intent == "emi":
            emi_result = call_emi_api(parsed)
            if emi_result is None:
                followup = call_llm([
                    {"role": "system", "content": base_assistant_prompt() +
                        " The user likely wants an EMI calculation but did not provide enough numbers. Ask them politely for loan amount, interest rate (per year), and tenure (years). Keep it short and friendly."},
                    {"role": "user", "content": user_msg},
                ])
                return ChatResponse(reply=followup)

            explanation = call_llm([
                {"role": "system", "content": base_assistant_prompt() +
                    " You already have the EMI calculation result from an internal API. Explain the result clearly in 1–2 short paragraphs and, if useful, a small bullet list. Do NOT show raw JSON."},
                {"role": "user", "content": json.dumps(emi_result)},
            ])
            return ChatResponse(reply=explanation)

        # SIP flow
        if intent == "sip":
            sip_result = call_sip_api(parsed)
            if sip_result is None:
                followup = call_llm([
                    {"role": "system", "content": base_assistant_prompt() +
                        " The user likely wants a SIP calculation but did not provide enough numbers. Ask for monthly amount, number of years, and (optionally) expected return %. Keep it short."},
                    {"role": "user", "content": user_msg},
                ])
                return ChatResponse(reply=followup)

            explanation = call_llm([
                {"role": "system", "content": base_assistant_prompt() +
                    " You already have the SIP calculation result from an internal API. Explain the result in 1–2 short paragraphs and a short bullet summary. Do NOT show raw JSON."},
                {"role": "user", "content": json.dumps(sip_result)},
            ])
            return ChatResponse(reply=explanation)

        # Mutual Fund / MF recommendation flow
        if intent == "mf":
            income_val = safe_float(parsed.get("income"))
            scheme_name = parsed.get("scheme_name")

            # If user provided a specific scheme name, try to fetch it from mfapi
            mf_meta = None
            mf_nav = None
            if scheme_name:
                mf_meta = mf_search_scheme(scheme_name)
                if mf_meta:
                    # Try get nav if meta includes code or schemeCode
                    scheme_code = mf_meta.get("schemeCode") or mf_meta.get("code") or mf_meta.get("scheme_code")
                    if scheme_code:
                        mf_nav = mf_get_nav_by_code(scheme_code)

            # If user gave income, generate an income-based suggestion
            if income_val:
                rec = recommend_mfs_by_income(income_val, top_n=5)
                # If we found mf_meta/nav for given scheme_name, attach to recommendation
                if mf_meta or mf_nav:
                    rec["found_scheme"] = mf_meta
                    rec["nav_data"] = mf_nav
                # Use LLM to craft final user-facing English reply (we pass rec)
                explanation = call_llm([
                    {"role": "system", "content": base_assistant_prompt() +
                        " Craft a concise English reply recommending SIP/Mutual Fund options based on the attached recommendation data. Keep it practical and include a short 'next steps' bullet list."},
                    {"role": "user", "content": json.dumps(rec)},
                ])
                return ChatResponse(reply=explanation)

            # If no income provided but scheme_name found -> give scheme info
            if mf_meta or mf_nav:
                # Craft an English explanation using fetched nav/meta
                explanation = call_llm([
                    {"role": "system", "content": base_assistant_prompt() +
                        " The user asked about a specific mutual fund. You have live MF data below. Explain in English the fund's recent NAV and what an investor should consider. Keep it short."},
                    {"role": "user", "content": json.dumps({"meta": mf_meta, "nav": mf_nav})},
                ])
                return ChatResponse(reply=explanation)

            # Otherwise ask for clarification (income or what kind of funds they want)
            followup = call_llm([
                {"role": "system", "content": base_assistant_prompt() +
                    " The user asked for mutual fund recommendations but did not give enough details. Ask for monthly budget or monthly SIP amount, investment horizon in years, and risk tolerance (low/medium/high). Keep it short and in English."},
                {"role": "user", "content": user_msg},
            ])
            return ChatResponse(reply=followup)

        # GENERAL finance chat (no tool calls)
        final_reply = call_llm([
            {"role": "system", "content": base_assistant_prompt()},
            {"role": "user", "content": user_msg},
        ])
        return ChatResponse(reply=final_reply)

    except Exception as e:
        print("Chat error:", e)
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
