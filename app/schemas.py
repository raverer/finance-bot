from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ============================================================
#                      EMI SCHEMAS
# ============================================================

class EMISingleRequest(BaseModel):
    principal: float = Field(..., gt=0)
    annual_rate: float = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)


class LoanInput(BaseModel):
    loan_type: Optional[str] = None
    principal: float = Field(..., gt=0)
    annual_rate: float = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)


class EMIMultiRequest(BaseModel):
    loans: List[LoanInput]
    monthly_income: Optional[float] = Field(None, gt=0)


class EMILoanResult(BaseModel):
    loan_type: Optional[str]
    emi: float
    principal: float
    annual_rate: float
    tenure_months: int


class EMIMultiResponse(BaseModel):
    loans: List[EMILoanResult]
    total_emi: float
    monthly_income: Optional[float] = None
    emi_to_income_ratio: Optional[float] = None
    risk_level: Optional[str] = None
    advice: Optional[str] = None


# ============================================================
#                      LEAD SCHEMAS
# ============================================================

class LeadBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    selected_service: Optional[str] = None
    income: Optional[float] = None
    financial_goal: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadResponse(LeadBase):
    id: int
    qualification_level: Optional[str] = None

    model_config = {
        "from_attributes": True  # replaces Pydantic v1 orm_mode
    }


# ============================================================
#                   APPOINTMENT SCHEMAS
# ============================================================

class AppointmentCreate(BaseModel):
    lead_id: int
    service: str
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    lead_id: int
    service: str
    date: str
    time: str
    status: str
    notes: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


# ============================================================
#                   SIP (Systematic Investment Plan)
# ============================================================

class SIPInput(BaseModel):
    scheme_code: Optional[str] = None
    scheme_name: Optional[str] = None

    monthly_amount: float
    years: float
    sip_day: int = Field(default=5, ge=1, le=28)
    expected_return: float = Field(default=12.0, ge=0)
    use_nav_history: bool = True


class SIPResult(BaseModel):
    scheme_name: str
    scheme_category: str
    scheme_type: str

    total_invested: float
    current_value: float
    profit: float
    absolute_return_percent: float
    annual_return_percent: float
    total_units: float
    latest_nav: float

# ============================================================
#                     CHAT / LLM SCHEMAS
# ============================================================

class ChatRequest(BaseModel):
    message: str
    context_type: Optional[str] = Field(
        default="general",
        description="one of: general, emi, sip"
    )


class ChatResponse(BaseModel):
    reply: str
