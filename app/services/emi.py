from typing import List, Optional, Tuple
from ..schemas import LoanInput, EMILoanResult


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Standard EMI formula:
    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    """
    r = annual_rate / 12 / 100  # monthly rate

    if r == 0:
        return round(principal / tenure_months, 2)

    emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
    return round(emi, 2)


def calculate_multi_emi(
    loans: List[LoanInput], monthly_income: Optional[float] = None
) -> Tuple[List[EMILoanResult], float, Optional[float], Optional[str], Optional[str]]:
    results: List[EMILoanResult] = []
    total_emi = 0.0

    for loan in loans:
        emi = calculate_emi(loan.principal, loan.annual_rate, loan.tenure_months)
        total_emi += emi
        results.append(
            EMILoanResult(
                loan_type=loan.loan_type,
                emi=emi,
                principal=loan.principal,
                annual_rate=loan.annual_rate,
                tenure_months=loan.tenure_months,
            )
        )

    emi_to_income_ratio = None
    risk_level = None
    advice = None

    if monthly_income and monthly_income > 0:
        emi_to_income_ratio = round((total_emi / monthly_income) * 100, 2)
        if emi_to_income_ratio <= 30:
            risk_level = "low"
            advice = (
                "Your EMI to income ratio is healthy. "
                "You can continue with current EMIs, but avoid taking new high-interest loans."
            )
        elif emi_to_income_ratio <= 50:
            risk_level = "medium"
            advice = (
                "Your EMI burden is moderate. Try to avoid new loans and consider prepaying high-interest loans when possible."
            )
        else:
            risk_level = "high"
            advice = (
                "Your EMI burden is high. Consider restructuring or prepaying some loans, "
                "reducing discretionary expenses, and avoiding any new debt."
            )

    return results, round(total_emi, 2), emi_to_income_ratio, risk_level, advice
