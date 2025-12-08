import React, { useState } from "react";
import { chatWithBot } from "../api/api";
import "./Chat.css";

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input) return;

    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    const botResponse = await chatWithBot(input);

    const botMsg = { sender: "bot", text: botResponse.response };
    setMessages((prev) => [...prev, botMsg]);

    setInput("");
  };

  return (
    <div className="chat-container">
      <h2>FinanceBot Chat</h2>

      <div className="chat-box">
        {messages.map((m, index) => (
          <div key={index} className={`message ${m.sender}`}>
            {m.text}
          </div>
        ))}
      </div>

      <div className="chat-input-box">
        <input
          value={input}
          placeholder="Ask something..."
          onChange={(e) => setInput(e.target.value)}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chatbot;
