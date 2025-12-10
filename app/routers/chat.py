from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse
import json
import os
import requests

# ============================================================
#   USE GROQ (cloud) – OLLAMA CANNOT RUN ON RAILWAY
# ============================================================

USE_OLLAMA = False   # IMPORTANT: keep this False on Railway

if USE_OLLAMA:
    from ..services.llm_ollama import call_llm_ollama as call_llm
else:
    from ..services.llm_groq import call_llm_groq as call_llm


router = APIRouter(prefix="/chat", tags=["Chat / LLM"])

# Internal base URL to call our own APIs (EMI, SIP) from inside the backend
INTERNAL_BASE = os.getenv("INTERNAL_BASE_URL", "http://127.0.0.1:8000")


# ============================================================
#  SYSTEM PROMPTS
# ============================================================

def base_assistant_prompt() -> str:
    return (
        "You are NiveshBuddy, a helpful Indian personal finance assistant. "
        "You simplify EMIs, SIPs, budgeting, and investments in simple language. "
        "You are NOT a SEBI-registered advisor; avoid specific stock tips. "
        "You can explain EMI and SIP math clearly for Indian users."
    )


def intent_extraction_prompt() -> str:
    """
    This prompt is used in the FIRST LLM call to decide what the user wants
    and extract numbers we can use for our APIs.
    """
    return (
        "You are a JSON parser for a finance chatbot.\n"
        "Your job is to:\n"
        "1) Detect the user's intent.\n"
        "2) Extract numeric parameters if present.\n\n"
        "Supported intents:\n"
        "- 'emi'  -> user wants EMI calculation / loan analysis\n"
        "- 'sip'  -> user wants SIP / monthly investing calculation\n"
        "- 'general' -> any other finance question or explanation\n\n"
        "Return STRICT JSON ONLY with this structure (no extra text):\n"
        "{\n"
        '  \"intent\": \"emi\" | \"sip\" | \"general\",\n'
        '  \"loan_amount\": float or null,\n'
        '  \"interest_rate\": float or null,            // annual %\n'
        '  \"tenure_years\": float or null,\n'
        '  \"monthly_amount\": float or null,\n'
        '  \"years\": float or null,\n'
        '  \"expected_return\": float or null,          // annual %\n'
        '  \"scheme_name\": string or null\n'
        "}\n\n"
        "If you are not sure about a value, use null.\n"
        "If intent is 'general', all numeric fields can be null.\n"
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


def call_emi_api(parsed: dict) -> dict | None:
    """
    Calls /emi/calculate IF we have enough data.
    Returns dict or None if we can't call.
    """
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
        res = requests.post(
            f"{INTERNAL_BASE}/emi/calculate",
            json=payload,
            timeout=15,
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("EMI API error:", e)
        return None


def call_sip_api(parsed: dict) -> dict | None:
    """
    Calls /sip/calculate IF we have enough data.
    Returns dict or None if we can't call.
    """
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
        res = requests.post(
            f"{INTERNAL_BASE}/sip/calculate",
            json=payload,
            timeout=25,
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("SIP API error:", e)
        return None


def run_intent_extraction(user_message: str) -> dict:
    """
    First LLM call: detect intent + extract parameters as JSON.
    Falls back to 'general' on any error.
    """
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
        }


# ============================================================
#  MAIN CHAT ENDPOINT
# ============================================================

@router.post("/", response_model=ChatResponse)
def chat_with_assistant(payload: ChatRequest):
    """
    Mixed mode:
    - Detect EMI / SIP / general intent.
    - If enough numbers -> call EMI/SIP APIs first, then explain result.
    - If not enough numbers -> ask user for missing info in a friendly way.
    """
    user_msg = payload.message

    try:
        # 1) Detect intent + extract params
        parsed = run_intent_extraction(user_msg)
        intent = parsed.get("intent", "general")

        # 2) If EMI intent
        if intent == "emi":
            emi_result = call_emi_api(parsed)
            if emi_result is None:
                # Not enough data -> ask for missing info
                followup = call_llm([
                    {
                        "role": "system",
                        "content": base_assistant_prompt()
                        + " The user likely wants an EMI calculation but did not provide enough numbers. "
                          "Ask them politely for loan amount, interest rate (per year), and tenure (years). "
                          "Keep it short and friendly.",
                    },
                    {"role": "user", "content": user_msg},
                ])
                return ChatResponse(reply=followup)

            # We HAVE EMI numbers + result → explain nicely
            explanation = call_llm([
                {
                    "role": "system",
                    "content": base_assistant_prompt()
                    + " You already have the EMI calculation result from an internal API. "
                      "Explain the result clearly in 1–2 short paragraphs and, if useful, a small bullet list. "
                      "Numbers from the API are in JSON here:\n"
                      f"{emi_result}\n"
                      "Do NOT show the raw JSON, just explain it in friendly language for an Indian user.",
                },
                {"role": "user", "content": user_msg},
            ])
            return ChatResponse(reply=explanation)

        # 3) If SIP intent
        if intent == "sip":
            sip_result = call_sip_api(parsed)
            if sip_result is None:
                # Not enough data -> ask for missing info
                followup = call_llm([
                    {
                        "role": "system",
                        "content": base_assistant_prompt()
                        + " The user likely wants a SIP calculation but did not provide enough numbers. "
                          "Ask them politely for monthly investment, number of years, and (optionally) expected return %. "
                          "Keep it short and friendly.",
                    },
                    {"role": "user", "content": user_msg},
                ])
                return ChatResponse(reply=followup)

            # We HAVE SIP data + result → explain nicely
            explanation = call_llm([
                {
                    "role": "system",
                    "content": base_assistant_prompt()
                    + " You already have the SIP calculation result from an internal API. "
                      "Explain the result clearly in 1–2 short paragraphs and a short bullet summary. "
                      "Numbers from the API are in JSON here:\n"
                      f"{sip_result}\n"
                      "Do NOT show the raw JSON, just explain it in friendly language for an Indian user.",
                },
                {"role": "user", "content": user_msg},
            ])
            return ChatResponse(reply=explanation)

        # 4) GENERAL finance chat (no tool calls)
        final_reply = call_llm([
            {"role": "system", "content": base_assistant_prompt()},
            {"role": "user", "content": user_msg},
        ])
        return ChatResponse(reply=final_reply)

    except Exception as e:
        print("Chat error:", e)
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
