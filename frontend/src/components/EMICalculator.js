import React, { useState } from "react";
import { calculateEmi } from "../api";

export default function EmiCalculator() {
  const [data, setData] = useState({
    amount: "",
    roi: "",
    tenure: ""
  });

  const [result, setResult] = useState(null);

  async function calc() {
    const res = await calculateEmi(data);
    setResult(res);
  }

  return (
    <div className="box">
      <h2>EMI Calculator</h2>
      <input placeholder="Loan Amount"
             onChange={e => setData({...data, amount: e.target.value})} />
      <input placeholder="Interest Rate"
             onChange={e => setData({...data, roi: e.target.value})} />
      <input placeholder="Tenure (months)"
             onChange={e => setData({...data, tenure: e.target.value})} />
      <button onClick={calc}>Calculate</button>

      {result && <p>EMI: ₹{result.emi}</p>}
    </div>
  );
}
