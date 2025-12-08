import React from "react";
import "./Home.css";
import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="home-container">
      <h1>Welcome to FinanceBot</h1>
      <p>Your personal finance assistant for EMI, SIP, Mutual Funds & Advice.</p>

      <div className="features-grid">
        <Link to="/emi" className="feature-card">
          <h3>📊 EMI Calculator</h3>
          <p>Calculate loan EMI instantly</p>
        </Link>

        <Link to="/sip" className="feature-card">
          <h3>📈 SIP Calculator</h3>
          <p>Plan monthly investments</p>
        </Link>

        <Link to="/funds" className="feature-card">
          <h3>💼 Mutual Funds</h3>
          <p>Search fund details & NAV</p>
        </Link>

        <Link to="/chat" className="feature-card">
          <h3>🤖 Chatbot</h3>
          <p>Ask any finance-related question</p>
        </Link>
      </div>
    </div>
  );
}

export default Home;
