import React from "react";
import Chatbot from "../components/Chatbot";

export default function Home() {
  return (
    <div className="container">
      <h1>Welcome to Finance Bot</h1>
      <p>Your personal AI-powered financial assistant.</p>

      <Chatbot />
    </div>
  );
}
