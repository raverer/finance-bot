import React from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <div style={{
      background: "#ffffff",
      padding: "20px",
      boxShadow: "0px 2px 8px rgba(0,0,0,0.1)",
      marginBottom: "20px"
    }}>
      <div className="container" style={{ display: "flex", justifyContent: "space-between" }}>
        <h2 style={{ margin: 0 }}>Finance Bot</h2>

        <div>
          <Link to="/" style={{ marginRight: 20 }}>Home</Link>
          <Link to="/tools" style={{ marginRight: 20 }}>Tools</Link>
        </div>
      </div>
    </div>
  );
}
