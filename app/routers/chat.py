from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse
import json
import os
import requests

# ============================================================
#   GROQ (cloud LLM) – ONLY OPTION FOR RAILWAY
# ============================================================

USE_OLLAMA = False   # MUST remain False on Railway

if USE_OLLAMA:
    from ..services.llm_ollama import call_llm_ollama as call_llm
else:
    from ..services.llm_groq import call_llm_groq as call_llm


router = APIRouter(prefix="/chat", tags=["Chat / LLM"])

# INTERNAL base URL to call our own APIs (SIP, EMI)
INTERNAL_BASE = os.getenv("INTERNAL_BASE_URL", "http://127.0.0.1:8000")


# ============================================================
#  SYSTEM PROMPTS
# ============================================================

def base_assistant_prompt() -> str:
    return (
        "You are NiveshBuddy, a helpful Indian personal finance assistant. "
        "You explain EMIs, loans, SIPs, and investments simply. "
        "Avoid stock tips; you are NOT a SEBI-registered advisor."
    )


def intent_extraction_prompt() -> str:
    return (
        "You are a JSON parser for a finance chatbot.\n"
        "Determine the user's intent and extract numbers.\n"
        "Valid intents: 'emi', 'sip', 'general'.\n\n"

        "Return STRICT JSON ONLY:\n"
        "{\n"
        '  "intent": "emi" | "sip" | "general",\n'
        '  "loan_amount": float or null,\n'
        '  "interest_rate": float or null,\n'
        '  "tenure_years": float or null,\n'
        '  "monthly_amount": float or null,\n'
        '  "years": float or null,\n'
        '  "expected_return": float or null,\n'
        '  "scheme_name": string or null\n'
        "}\n\n"
        "If unsure → use null. If unrelated → intent should be 'general'."
    )


# ============================================================
#  HELPERS
# ============================================================

def safe_float(v):
    try:
        return float(v) if v is not None else None
    except:
        return None


def call_emi_api(parsed):
    loan = safe_float(parsed.get("loan_amount"))
    rate = safe_float(parsed.get("interest_rate"))
    years = safe_float(parsed.get("tenure_years"))

    if None in (loan, rate, years):
        return None

    payload = {
        "loan_amount": loan,
        "annual_interest_rate": rate,
        "tenure_years": years,
    }

    try:
        r = requests.post(f"{INTERNAL_BASE}/emi/calculate", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("EMI API error:", e)
        return None


def call_sip_api(parsed):
    monthly = safe_float(parsed.get("monthly_amount"))
    years = safe_float(parsed.get("years"))
    expected = safe_float(parsed.get("expected_return"))
    scheme_name = parsed.get("scheme_name")

    if monthly is None or years is None:
        return None

    payload = {
        "scheme_code": None,
        "scheme_name": scheme_name,
        "monthly_amount": monthly,
        "years": years,
        "sip_day": 5,
        "expected_return": expected if expected is not None else 12,
        "use_nav_history": True,
    }

    try:
        r = requests.post(f"{INTERNAL_BASE}/sip/calculate", json=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("SIP API error:", e)
        return None


def run_intent_extraction(msg: str):
    system_prompt = intent_extraction_prompt()

    llm_raw = call_llm([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": msg},
    ])

    try:
        parsed = json.loads(llm_raw)
        if "intent" not in parsed:
            raise ValueError("Missing intent")
        return parsed

    except Exception as e:
        print("Intent parse error:", e, "LLM returned:", llm_raw)
        return {
            "intent": "general",
            "loan_amount": None,
            "interest_rate": None,
            "tenure_years": None,
            "monthly_amount": None,
            "years": None,
            "expected_return": None,
            "scheme_name": None,
        }


# ============================================================
#  MAIN CHAT ENDPOINT
# ============================================================

@router.post("/", response_model=ChatResponse)
def chat_with_assistant(payload: ChatRequest):
    user_msg = payload.message

    try:
        # Step 1 → intent + number extraction
        parsed = run_intent_extraction(user_msg)
        intent = parsed["intent"]

        # ------------------------------------------------------
        #  EMI FLOW
        # ------------------------------------------------------
        if intent == "emi":
            result = call_emi_api(parsed)

            if result is None:
                # Not enough numbers → ask politely
                ask = call_llm([
                    {
                        "role": "system",
                        "content": base_assistant_prompt()
                        + "User wants an EMI calculation. Ask for missing details: "
                          "loan amount, annual interest %, and tenure in years."
                    },
                    {"role": "user", "content": user_msg},
                ])
                return ChatResponse(reply=ask)

            # We HAVE the EMI result → explain it
            explain = call_llm([
                {
                    "role": "system",
                    "content": base_assistant_prompt()
                    + f"You have EMI calculation results here: {result}\n"
                      "Explain these numbers clearly, simply, without showing raw JSON."
                },
                {"role": "user", "content": user_msg},
            ])
            return ChatResponse(reply=explain)

        # ------------------------------------------------------
        #  SIP FLOW
        # ------------------------------------------------------
        if intent == "sip":
            result = call_sip_api(parsed)

            if result is None:
                ask = call_llm([
                    {
                        "role": "system",
                        "content": base_assistant_prompt()
                        + "User wants a SIP calculation. Ask for monthly amount and years. "
                          "Optionally ask for expected return %."
                    },
                    {"role": "user", "content": user_msg},
                ])
                return ChatResponse(reply=ask)

            explain = call_llm([
                {
                    "role": "system",
                    "content": base_assistant_prompt()
                    + f"You have SIP results here: {result}\n"
                      "Explain them simply without showing JSON. Include future value / invested amount summary."
                },
                {"role": "user", "content": user_msg},
            ])
            return ChatResponse(reply=explain)

        # ------------------------------------------------------
        #  GENERAL FINANCE CHAT
        # ------------------------------------------------------
        reply = call_llm([
            {"role": "system", "content": base_assistant_prompt()},
            {"role": "user", "content": user_msg},
        ])
        return ChatResponse(reply=reply)

    except Exception as e:
        print("Chat error:", e)
        raise HTTPException(status_code=500, detail=str(e))
