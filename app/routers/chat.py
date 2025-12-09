from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse
from ..services.llm_groq import call_llm_groq

router = APIRouter(
    prefix="/chat",
    tags=["Chat / LLM"],
    strict_slashes=False
)
# Force cloud LLM because Railway cannot run Ollama
USE_OLLAMA = False  


def build_system_prompt(context_type: str) -> str:
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

    base += (
        " If the user provides numbers (salary, EMI, SIP, goals), explain the math clearly "
        "and avoid giving unrealistic promises or guaranteed returns."
    )

    return base


@router.post("/", response_model=ChatResponse)
def chat_with_assistant(payload: ChatRequest):
    """
    POST /chat
    Input:  { "message": "...", "context_type": "general" }
    Output: { "reply": "..." }
    """

    try:
        # Build the system instruction
        system_prompt = build_system_prompt(payload.context_type)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": payload.message},
        ]

        # ALWAYS use Groq on Railway
        reply = call_llm_groq(messages)

        if not reply:
            raise ValueError("Empty response from LLM")

        return ChatResponse(reply=reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
