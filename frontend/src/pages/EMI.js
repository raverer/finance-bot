import React, { useState } from "react";
import { calculateEMI } from "../api/api";

function EMI() {
  const [form, setForm] = useState({
    loanAmount: "",
    interestRate: "",
    tenureMonths: ""
  });

  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setForm({...form, [e.target.name]: e.target.value});
  };

  const submit = async () => {
    const res = await calculateEMI(form);
    setResult(res);
  };

  return (
    <div className="container">
      <h2>EMI Calculator</h2>

      <input
        type="number"
        placeholder="Loan Amount"
        name="loanAmount"
        onChange={handleChange}
      />

      <input
        type="number"
        placeholder="Interest Rate (%)"
        name="interestRate"
        onChange={handleChange}
      />

      <input
        type="number"
        placeholder="Tenure (Months)"
        name="tenureMonths"
        onChange={handleChange}
      />

      <button onClick={submit}>Calculate EMI</button>

      {result && (
        <div className="result-card">
          <p><strong>Monthly EMI:</strong> ₹{result.emi}</p>
          <p><strong>Total Interest:</strong> ₹{result.totalInterest}</p>
          <p><strong>Total Amount:</strong> ₹{result.totalPayment}</p>
        </div>
      )}
    </div>
  );
}

export default EMI;
