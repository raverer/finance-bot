import React, { useState } from "react";
import { searchFund } from "../api/api";

function MutualFunds() {
  const [query, setQuery] = useState("");
  const [fund, setFund] = useState(null);

  const submit = async () => {
    const res = await searchFund(query);
    setFund(res);
  };

  return (
    <div className="container">
      <h2>Search Mutual Funds</h2>

      <input
        type="text"
        placeholder="Enter fund name"
        onChange={(e) => setQuery(e.target.value)}
      />

      <button onClick={submit}>Search</button>

      {fund && (
        <div className="result-card">
          <h3>{fund.schemeName}</h3>
          <p><strong>NAV:</strong> {fund.nav}</p>
          <p><strong>Category:</strong> {fund.category}</p>
        </div>
      )}
    </div>
  );
}

export default MutualFunds;
