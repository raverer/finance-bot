import React from "react";
import Chat from "./Chat";
import "./styles.css";

<header className="app-header">
  <h1>NiveshBuddy – Your AI Finance Partner</h1>
  <p className="subtitle">Smart EMI, SIP & Mutual Fund guidance for India</p>
</header>

function App() {
  return (
    <div className="app-container">
      <h1 className="title">Finance Bot</h1>
      <Chat />
    </div>
  );
}

export default App;
