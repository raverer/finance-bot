from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse
import os, json, requests

# ==============================
# CONFIG
# ==============================

USE_OLLAMA = False  # MUST be False on Railway

if USE_OLLAMA:
    from ..services.llm_ollama import call_llm_ollama as call_llm
else:
    from ..services.llm_groq import call_llm_groq as call_llm

router = APIRouter(prefix="/chat", tags=["Chat"])

INTERNAL_BASE = os.getenv("INTERNAL_BASE_URL", "http://127.0.0.1:8000")

# ==============================
# MUTUAL FUND MASTER LIST (OPTION B)
# ==============================

MF_RECOMMENDATIONS = {
    "large_cap": [
        {"name": "Axis Bluechip Fund", "code": "120465"},
        {"name": "Mirae Asset Large Cap Fund", "code": "118834"},
    ],
    "flexi_cap": [
        {"name": "Parag Parikh Flexi Cap Fund", "code": "122639"},
        {"name": "Kotak Flexicap Fund", "code": "118550"},
    ],
    "elss": [
        {"name": "Mirae Asset Tax Saver Fund", "code": "125497"},
        {"name": "Quant ELSS Tax Saver Fund", "code": "120847"},
    ],
    "index": [
        {"name": "UTI Nifty 50 Index Fund", "code": "120716"},
    ]
}

# ==============================
# SYSTEM PROMPT (ENGLISH ONLY)
# ==============================

def system_prompt():
    return (
        "You are NiveshBuddy, an Indian personal finance assistant. "
        "Always respond in clear, simple English only. "
        "You help users with SIPs, EMIs, budgeting, and mutual funds. "
        "You are NOT a SEBI-registered advisor. Avoid stock tips or promises. "
        "Be practical, friendly, and concise."
    )

# ==============================
# HELPERS
# ==============================

def fetch_nav(scheme_code):
    try:
        res = requests.get(f"https://api.mfapi.in/mf/{scheme_code}", timeout=10)
        data = res.json()
        return data["data"][0]["nav"]
    except:
        return "N/A"


def suggest_sip_from_income(income):
    if income < 30000:
        return round(income * 0.07)
    elif income <= 80000:
        return round(income * 0.12)
    else:
        return round(income * 0.18)


# ==============================
# MAIN CHAT ENDPOINT
# ==============================

@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest):
    user_msg = payload.message.lower()

    try:
        # ---------- SIP FROM INCOME ----------
        if "income" in user_msg and "sip" in user_msg:
            income = int("".join(filter(str.isdigit, user_msg)))
            sip_amount = suggest_sip_from_income(income)

            fund_lines = []
            for category, funds in MF_RECOMMENDATIONS.items():
                fund = funds[0]
                nav = fetch_nav(fund["code"])
                fund_lines.append(f"- {fund['name']} (NAV ₹{nav})")

            reply = (
                f"Based on your monthly income of ₹{income}, a healthy SIP amount "
                f"would be around ₹{sip_amount} per month.\n\n"
                "Here are some good mutual fund options you can consider:\n"
                + "\n".join(fund_lines) +
                "\n\nYou can split your SIP across 2–3 funds and invest for at least 5–10 years."
            )
            return ChatResponse(reply=reply)

        # ---------- EMI ----------
        if "emi" in user_msg:
            res = requests.post(
                f"{INTERNAL_BASE}/emi/calculate",
                json=payload.dict(),
                timeout=15
            )
            return ChatResponse(reply=str(res.json()))

        # ---------- SIP CALC ----------
        if "sip" in user_msg and any(char.isdigit() for char in user_msg):
            res = requests.post(
                f"{INTERNAL_BASE}/sip/calculate",
                json=payload.dict(),
                timeout=15
            )
            return ChatResponse(reply=str(res.json()))

        # ---------- GENERAL CHAT ----------
        llm_reply = call_llm([
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": payload.message}
        ])
        return ChatResponse(reply=llm_reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
