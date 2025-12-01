from fastapi import APIRouter
from ..schemas import EMISingleRequest, EMIMultiRequest, EMIMultiResponse
from ..services.emi import calculate_emi, calculate_multi_emi

router = APIRouter(prefix="/emi", tags=["EMI"])


@router.post("/single")
def calculate_single_emi(payload: EMISingleRequest):
    emi = calculate_emi(
        principal=payload.principal,
        annual_rate=payload.annual_rate,
        tenure_months=payload.tenure_months,
    )
    return {
        "emi": emi,
        "principal": payload.principal,
        "annual_rate": payload.annual_rate,
        "tenure_months": payload.tenure_months,
    }


@router.post("/multi", response_model=EMIMultiResponse)
def calculate_multi(payload: EMIMultiRequest):
    loans, total_emi, ratio, risk_level, advice = calculate_multi_emi(
        loans=payload.loans, monthly_income=payload.monthly_income
    )
    return EMIMultiResponse(
        loans=loans,
        total_emi=total_emi,
        monthly_income=payload.monthly_income,
        emi_to_income_ratio=ratio,
        risk_level=risk_level,
        advice=advice,
    )
