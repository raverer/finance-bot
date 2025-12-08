import React, { useState } from "react";
import { calculateSIP } from "../api/api";

function SIP() {
  const [form, setForm] = useState({
    monthlyInvestment: "",
    years: "",
    expectedReturn: ""
  });

  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setForm({...form, [e.target.name]: e.target.value});
  };

  const submit = async () => {
    const res = await calculateSIP(form);
    setResult(res);
  };

  return (
    <div className="container">
      <h2>SIP Calculator</h2>

      <input
        type="number"
        name="monthlyInvestment"
        placeholder="Monthly SIP Amount"
        onChange={handleChange}
      />

      <input
        type="number"
        name="years"
        placeholder="Investment Duration (Years)"
        onChange={handleChange}
      />

      <input
        type="number"
        name="expectedReturn"
        placeholder="Expected Return (%)"
        onChange={handleChange}
      />

      <button onClick={submit}>Calculate SIP</button>

      {result && (
        <div className="result-card">
          <p><strong>Total Invested:</strong> ₹{result.totalInvested}</p>
          <p><strong>Estimated Returns:</strong> ₹{result.totalReturns}</p>
          <p><strong>Maturity Amount:</strong> ₹{result.maturityAmount}</p>
        </div>
      )}
    </div>
  );
}

export default SIP;
