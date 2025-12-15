from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse
import json
import os
import requests

# ============================================================
#  LLM SELECTION (GROQ FOR CLOUD)
# ============================================================

from ..services.llm_groq import call_llm_groq as call_llm

router = APIRouter(prefix="/chat", tags=["Chat / LLM"])

INTERNAL_BASE = os.getenv("INTERNAL_BASE_URL", "http://127.0.0.1:8000")

# ============================================================
#  SYSTEM PROMPTS
# ============================================================

def base_prompt() -> str:
    return (
        "You are NiveshBuddy, a modern Indian personal finance assistant.\n"
        "Rules:\n"
        "- Reply ONLY in clear, simple English.\n"
        "- Be conversational and friendly.\n"
        "- Do NOT mention NAV numbers unless explicitly asked.\n"
        "- Prefer Direct mutual fund plans.\n"
        "- Never give stock tips or guaranteed returns.\n"
        "- Education-first, SEBI-safe tone.\n"
        "- Think like a fintech product used in India in 2025.\n"
    )


def intent_prompt() -> str:
    return (
        "You are a JSON-only intent extractor.\n\n"
        "Identify intent and extract numbers from the user's message.\n\n"
        "Intents:\n"
        "- emi\n"
        "- sip\n"
        "- mutual_fund_info\n"
        "- general\n\n"
        "Return ONLY valid JSON:\n"
        "{\n"
        '  "intent": "emi" | "sip" | "mutual_fund_info" | "general",\n'
        '  "income": number | null,\n'
        '  "loan_amount": number | null,\n'
        '  "interest_rate": number | null,\n'
        '  "tenure_years": number | null,\n'
        '  "monthly_amount": number | null,\n'
        '  "years": number | null,\n'
        '  "fund_name": string | null\n'
        "}\n"
    )

# ============================================================
#  HELPERS
# ============================================================

def safe_float(v):
    try:
        return float(v) if v is not None else None
    except:
        return None


def calculate_sip_budget(income: float) -> int:
    return int(income * 0.12)  # 10–15% rule, conservative


def call_emi_api(parsed):
    if not all([parsed["loan_amount"], parsed["interest_rate"], parsed["tenure_years"]]):
        return None

    payload = {
        "loan_amount": parsed["loan_amount"],
        "annual_interest_rate": parsed["interest_rate"],
        "tenure_years": parsed["tenure_years"],
    }

    try:
        r = requests.post(f"{INTERNAL_BASE}/emi/calculate", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return None


def call_sip_api(parsed):
    if not all([parsed["monthly_amount"], parsed["years"]]):
        return None

    payload = {
        "monthly_amount": parsed["monthly_amount"],
        "years": parsed["years"],
        "expected_return": 12,
        "use_nav_history": True,
    }

    try:
        r = requests.post(f"{INTERNAL_BASE}/sip/calculate", json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except:
        return None


def run_intent_detection(message: str) -> dict:
    try:
        raw = call_llm([
            {"role": "system", "content": intent_prompt()},
            {"role": "user", "content": message}
        ])
        return json.loads(raw)
    except:
        return {"intent": "general"}

# ============================================================
#  MAIN CHAT ENDPOINT
# ============================================================

@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest):
    try:
        parsed = run_intent_detection(payload.message)
        intent = parsed.get("intent", "general")

        # ---------------- EMI ----------------
        if intent == "emi":
            emi_data = call_emi_api(parsed)

            if not emi_data:
                reply = call_llm([
                    {"role": "system", "content": base_prompt() +
                     "Ask politely for loan amount, interest rate (annual), and tenure in years."},
                    {"role": "user", "content": payload.message}
                ])
                return ChatResponse(reply=reply)

            explanation = call_llm([
                {"role": "system", "content": base_prompt() +
                 f"Explain this EMI result in simple English:\n{emi_data}\n"
                 "Do not show formulas or JSON. Keep it clear and short."},
                {"role": "user", "content": payload.message}
            ])
            return ChatResponse(reply=explanation)

        # ---------------- SIP ----------------
        if intent == "sip":
            income = safe_float(parsed.get("income"))

            if income:
                sip_budget = calculate_sip_budget(income)
                reply = call_llm([
                    {"role": "system", "content": base_prompt() +
                     f"The user's income is ₹{income}. "
                     f"Suggest SIP budget around ₹{sip_budget}. "
                     "Recommend diversified mutual fund categories (not NAVs). "
                     "Mention Direct plans. No specific guarantees."},
                    {"role": "user", "content": payload.message}
                ])
                return ChatResponse(reply=reply)

            sip_data = call_sip_api(parsed)
            if sip_data:
                explanation = call_llm([
                    {"role": "system", "content": base_prompt() +
                     f"Explain this SIP outcome clearly:\n{sip_data}\n"
                     "Focus on long-term investing benefits."},
                    {"role": "user", "content": payload.message}
                ])
                return ChatResponse(reply=explanation)

            reply = call_llm([
                {"role": "system", "content": base_prompt() +
                 "Ask politely for monthly SIP amount and investment duration."},
                {"role": "user", "content": payload.message}
            ])
            return ChatResponse(reply=reply)

        # ----------- MUTUAL FUND INFO ----------
        if intent == "mutual_fund_info":
            reply = call_llm([
                {"role": "system", "content": base_prompt() +
                 "Explain this mutual fund in an educational way. "
                 "Do not recommend buying or selling. "
                 "Explain category, suitability, and risks."},
                {"role": "user", "content": payload.message}
            ])
            return ChatResponse(reply=reply)

        # ---------------- GENERAL --------------
        final_reply = call_llm([
            {"role": "system", "content": base_prompt()},
            {"role": "user", "content": payload.message}
        ])
        return ChatResponse(reply=final_reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
