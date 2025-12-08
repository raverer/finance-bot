import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-logo">FinanceBot</div>

      <ul className="navbar-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/emi">EMI Calculator</Link></li>
        <li><Link to="/sip">SIP Calculator</Link></li>
        <li><Link to="/funds">Mutual Funds</Link></li>
        <li><Link to="/chat">Chatbot</Link></li>
      </ul>
    </nav>
  );
}

export default Navbar;
