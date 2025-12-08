import React, { useState } from "react";
import { calculateSip } from "../api";

export default function SipCalculator() {
  const [data, setData] = useState({
    scheme_name: "",
    monthly_investment: "",
    years: ""
  });

  const [result, setResult] = useState(null);

  async function calc() {
    const res = await calculateSip(data);
    setResult(res);
  }

  return (
    <div className="box">
      <h2>SIP Calculator</h2>
      <input placeholder="Scheme Name"
             onChange={e => setData({...data, scheme_name: e.target.value})} />
      <input placeholder="Monthly Investment"
             onChange={e => setData({...data, monthly_investment: e.target.value})} />
      <input placeholder="Years"
             onChange={e => setData({...data, years: e.target.value})} />
      <button onClick={calc}>Calculate</button>

      {result && (
        <div>
          <p>Total Invested: ₹{result.total_invested}</p>
          <p>Expected Returns: ₹{result.expected_return}</p>
        </div>
      )}
    </div>
  );
}
