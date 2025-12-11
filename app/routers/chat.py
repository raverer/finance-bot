from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse
import json
import os
import requests
import re

# ============================================================
#   ALWAYS USE GROQ ON RAILWAY
# ============================================================

USE_OLLAMA = False

if USE_OLLAMA:
    from ..services.llm_ollama import call_llm_ollama as call_llm
else:
    from ..services.llm_groq import call_llm_groq as call_llm


router = APIRouter(prefix="/chat", tags=["Chat / LLM"])

# Internal base URL for calling EMI/SIP services FROM backend
INTERNAL_BASE = os.getenv("INTERNAL_BASE_URL", "http://127.0.0.1:8000")

# ============================================================
#  SYSTEM PROMPTS
# ============================================================

def base_assistant_prompt() -> str:
    return (
        "You are NiveshBuddy, a friendly Indian personal finance assistant. "
        "You ALWAYS respond ONLY in English. "
        "Your tone is simple, clear, and easy for beginners. "
        "You explain EMIs, SIPs, budgeting, loans, and investment basics in plain English. "
        "You are NOT a SEBI-registered advisor, so avoid giving stock tips. "
        "Do not use Hindi or Hinglish. Use English only."
    )


def intent_extraction_prompt() -> str:
    return (
        "You are a JSON parser for a finance chatbot.\n"
        "Extract user intent and numbers.\n\n"
        "INTENTS:\n"
        "- 'emi' → EMI calculation or loan query\n"
        "- 'sip' → SIP / investment calculation\n"
        "- 'general' → any other finance question\n\n"
        "Extract numbers even if written as text like '5 lakh', '10%', '5 years'.\n\n"
        "RETURN STRICT JSON ONLY:\n"
        "{\n"
        "  \"intent\": \"emi\" | \"sip\" | \"general\",\n"
        "  \"loan_amount\": number or null,\n"
        "  \"interest_rate\": number or null,\n"
        "  \"tenure_years\": number or null,\n"
        "  \"monthly_amount\": number or null,\n"
        "  \"years\": number or null,\n"
        "  \"expected_return\": number or null,\n"
        "  \"scheme_name\": string or null\n"
        "}\n\n"
        "If unsure, return null for that field.\n"
        "Make sure JSON is valid. No explanation outside JSON."
    )


# ============================================================
#  NUMBER NORMALIZATION HELPERS
# ============================================================

def safe_float(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        v = value.lower().strip()
        v = v.replace("rs", "").replace("₹", "").replace(",", "")

        # lakh → 100,000
        if "lakh" in v or "lac" in v:
            num = re.findall(r"[\d\.]+", v)
            return float(num[0]) * 100000 if num else None

        # crore → 10,000,000
        if "crore" in v:
            num = re.findall(r"[\d\.]+", v)
            return float(num[0]) * 10000000 if num else None

        # Remove % sign
        v = v.replace("%", "")

        # Extract a normal number
        nums = re.findall(r"[\d\.]+", v)
        if nums:
            return float(nums[0])

    return None


# ============================================================
#  EMI API CALL
# ============================================================

def call_emi_api(parsed: dict):
    loan_amount = safe_float(parsed.get("loan_amount"))
    interest_rate = safe_float(parsed.get("interest_rate"))
    tenure_years = safe_float(parsed.get("tenure_years"))

    # All 3 required
    if not (loan_amount and interest_rate and tenure_years):
        return None

    payload = {
        "loan_amount": loan_amount,
        "annual_interest_rate": interest_rate,
        "tenure_years": tenure_years,
    }

    try:
        res = requests.post(f"{INTERNAL_BASE}/emi/calculate", json=payload, timeout=20)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("EMI API error:", e)
        return None


# ============================================================
#  SIP API CALL
# ============================================================

def call_sip_api(parsed: dict):
    monthly_amount = safe_float(parsed.get("monthly_amount"))
    years = safe_float(parsed.get("years"))
    expected_return = safe_float(parsed.get("expected_return"))
    scheme_name = parsed.get("scheme_name")

    if not (monthly_amount and years):
        return None

    payload = {
        "scheme_code": None,
        "scheme_name": scheme_name,
        "monthly_amount": monthly_amount,
        "years": years,
        "sip_day": 5,
        "expected_return": expected_return if expected_return else 12,
        "use_nav_history": True,
    }

    try:
        res = requests.post(f"{INTERNAL_BASE}/sip/calculate", json=payload, timeout=25)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("SIP API error:", e)
        return None


# ============================================================
#  INTENT EXTRACTION (FIRST LLM CALL)
# ============================================================

def run_intent_extraction(message: str):
    system_prompt = intent_extraction_prompt()

    llm_reply = call_llm([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ])

    try:
        parsed = json.loads(llm_reply)
        if "intent" not in parsed:
            raise ValueError("Missing intent")
        return parsed
    except Exception as e:
        print("Intent parse error:", e, llm_reply)
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
        parsed = run_intent_extraction(user_msg)
        intent = parsed.get("intent", "general")

        # ========================
        #        EMI LOGIC
        # ========================
        if intent == "emi":
            emi_data = call_emi_api(parsed)

            if emi_data:
                explanation = call_llm([
                    {
                        "role": "system",
                        "content": base_assistant_prompt()
                        + "Explain this EMI calculation result in simple language:\n"
                        f"{emi_data}\n"
                        "Do NOT show raw JSON. Only explain cleanly.",
                    },
                    {"role": "user", "content": user_msg},
                ])
                return ChatResponse(reply=explanation)

            # Not enough numbers → ask user
            ask = call_llm([
                {
                    "role": "system",
                    "content": base_assistant_prompt()
                    + "User wants EMI calculation but hasn't given enough numbers. "
                      "Ask them for loan amount, interest rate, and tenure.",
                },
                {"role": "user", "content": user_msg},
            ])
            return ChatResponse(reply=ask)

        # ========================
        #        SIP LOGIC
        # ========================
        if intent == "sip":
            sip_data = call_sip_api(parsed)

            if sip_data:
                explanation = call_llm([
                    {
                        "role": "system",
                        "content": base_assistant_prompt()
                        + "Explain this SIP simulation result clearly:\n"
                        f"{sip_data}\n"
                        "Do NOT show the raw JSON.",
                    },
                    {"role": "user", "content": user_msg},
                ])
                return ChatResponse(reply=explanation)

            # Not enough numbers → ask user
            ask = call_llm([
                {
                    "role": "system",
                    "content": base_assistant_prompt()
                    + "User wants SIP calculation but didn't give enough numbers. "
                      "Ask for monthly amount, years, and expected return.",
                },
                {"role": "user", "content": user_msg},
            ])
            return ChatResponse(reply=ask)

        # ========================
        #   GENERAL FINANCE CHAT
        # ========================
        general_reply = call_llm([
            {"role": "system", "content": base_assistant_prompt()},
            {"role": "user", "content": user_msg},
        ])
        return ChatResponse(reply=general_reply)

    except Exception as e:
        print("Chat Error:", e)
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
