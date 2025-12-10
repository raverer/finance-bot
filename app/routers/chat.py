from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse

# ============================================================
#   SWITCH TOGGLE: Choose between OLLAMA (local) or GROQ (cloud)
# ============================================================

USE_OLLAMA = False   # <-- IMPORTANT: OLLAMA CANNOT RUN ON RAILWAY

if USE_OLLAMA:
    from ..services.llm_ollama import call_llm_ollama as call_llm
else:
    from ..services.llm_groq import call_llm_groq as call_llm


router = APIRouter(prefix="/chat", tags=["Chat / LLM"])


def build_system_prompt(context_type: str) -> str:
    base = (
        "You are NiveshBuddy, a helpful Indian personal finance assistant. "
        "You simplify EMIs, SIPs, budgeting, and investment basics. "
        "You are NOT a SEBI-registered advisor; avoid giving specific stock recommendations."
    )
    return base


@router.post("/", response_model=ChatResponse)
def chat_with_assistant(payload: ChatRequest):
    try:
        system_prompt = build_system_prompt(payload.context_type)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": payload.message},
        ]

        reply = call_llm(messages)   # <-- This WILL use Groq now

        return ChatResponse(reply=reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
