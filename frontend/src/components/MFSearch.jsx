import React, { useState } from "react";
import { fetchFund } from "../api/api";

export default function MFSearch() {
  const [name, setName] = useState("");
  const [details, setDetails] = useState(null);

  const search = async () => {
    const data = await fetchFund(name);
    setDetails(data);
  };

  return (
    <div className="form-box">
      <h3>Mutual Fund Lookup</h3>

      <input
        placeholder="Mutual Fund Name"
        value={name}
        onChange={e => setName(e.target.value)}
      />
      <button onClick={search}>Search</button>

      {details && (
        <pre>{JSON.stringify(details, null, 2)}</pre>
      )}
    </div>
  );
}
