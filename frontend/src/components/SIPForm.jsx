import React, { useState } from "react";
import { calculateSIP } from "../api/api";

export default function SIPForm() {
  const [data, setData] = useState({
    scheme_name: "",
    monthly_amount: "",
    tenure_years: ""
  });

  const [result, setResult] = useState(null);

  const handleChange = e => {
    setData({ ...data, [e.target.name]: e.target.value });
  };

  const calculate = async () => {
    const response = await calculateSIP(data);
    setResult(response);
  };

  return (
    <div className="form-box">
      <h3>SIP Calculator</h3>

      <input
        name="scheme_name"
        placeholder="Mutual Fund Name"
        onChange={handleChange}
      />
      <input
        name="monthly_amount"
        placeholder="Monthly Amount"
        onChange={handleChange}
      />
      <input
        name="tenure_years"
        placeholder="Tenure (Years)"
        onChange={handleChange}
      />

      <button onClick={calculate}>Calculate SIP</button>

      {result && (
        <div>
          <p><strong>Total Investment:</strong> ₹{result.total_invested}</p>
          <p><strong>Estimated Corpus:</strong> ₹{result.estimated_returns}</p>
        </div>
      )}
    </div>
  );
}
