import React, { useState } from "react";
import { calculateEMI } from "../api/api";

export default function EMIForm() {
  const [data, setData] = useState({
    loanAmount: "",
    interestRate: "",
    tenureMonths: ""
  });
  
  const [result, setResult] = useState(null);

  const handleChange = e => {
    setData({ ...data, [e.target.name]: e.target.value });
  };

  const calculate = async () => {
    const response = await calculateEMI(data);
    setResult(response);
  };

  return (
    <div className="form-box">
      <h3>EMI Calculator</h3>

      <input
        name="loanAmount"
        placeholder="Loan Amount"
        onChange={handleChange}
      />
      <input
        name="interestRate"
        placeholder="Interest Rate (%)"
        onChange={handleChange}
      />
      <input
        name="tenureMonths"
        placeholder="Tenure (Months)"
        onChange={handleChange}
      />

      <button onClick={calculate}>Calculate EMI</button>

      {result && (
        <p><strong>EMI:</strong> ₹{result.emi}</p>
      )}
    </div>
  );
}
