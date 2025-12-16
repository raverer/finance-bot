import React from "react";
import Chat from "./Chat";
import "./styles.css";

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>NiveshBuddy</h1>
        <p>
          AI-powered personal finance assistant for SIPs, EMIs & mutual funds
        </p>
      </header>

      <Chat />

      <footer className="app-footer">
        Educational purpose only • Not SEBI registered • India 🇮🇳
      </footer>
    </div>
  );
}

export default App;
