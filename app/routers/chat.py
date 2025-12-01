from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse

# ============================================================
#   SWITCH TOGGLE: Choose between OLLAMA (local) or GROQ (cloud)
# ============================================================
USE_OLLAMA = True   # ⬅️ Change to False when deploying online

if USE_OLLAMA:
    from ..services.llm_ollama import call_llm_ollama as call_llm
else:
    from ..services.llm_groq import call_llm_groq as call_llm

# ============================================================
#                   CHAT ROUTER
# ============================================================

router = APIRouter(prefix="/chat", tags=["Chat / LLM"])


def build_system_prompt(context_type: str) -> str:
    """
    Creates a context-aware system prompt for the finance assistant.
    """
    base = (
        "You are NiveshBuddy, a helpful Indian personal finance assistant. "
        "You simplify EMIs, SIPs, budgeting, and investment basics. "
        "You are NOT a SEBI-registered advisor; avoid giving specific stock recommendations. "
        "Explain concepts simply, guide users on safe decision-making, "
        "and ask clarifying questions when needed."
    )

    if context_type == "emi":
        base += (
            " Focus on EMI analysis, EMI-to-income ratio, safe vs risky levels, "
            "loan management guidance, and debt reduction strategies."
        )
    elif context_type == "sip":
        base += (
            " Focus on SIP investing, long-term planning, compounding, and "
            "understanding equity vs debt funds based on risk appetite."
        )
    else:
        base += (
            " You may freely answer general finance queries as well."
        )

    base += (
        " If the user provides numbers (salary, EMI, SIP, goals), explain the math clearly "
        "and avoid giving unrealistic promises or guaranteed returns."
    )

    return base


@router.post("/", response_model=ChatResponse)
def chat_with_assistant(payload: ChatRequest):
    """
    Main chat endpoint.
    Uses either Ollama (local) or Groq (cloud) depending on USE_OLLAMA flag.
    """
    try:
        system_prompt = build_system_prompt(payload.context_type)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": payload.message},
        ]

        reply = call_llm(messages)

        return ChatResponse(reply=reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
