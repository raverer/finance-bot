import React, { useState } from "react";
import { chat } from "../api/api";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input) return;
    const userMessage = { sender: "user", text: input };
    setMessages([...messages, userMessage]);

    const response = await chat(input);
    const botMessage = { sender: "bot", text: response.reply };

    setMessages(prev => [...prev, botMessage]);
    setInput("");
  };

  return (
    <div className="form-box">
      <h3>Chat with Finance Bot</h3>

      <div style={{ height: "200px", overflowY: "scroll", background: "#f0f0f0", padding: 10 }}>
        {messages.map((msg, i) => (
          <p key={i} style={{ textAlign: msg.sender === "user" ? "right" : "left" }}>
            <strong>{msg.sender === "user" ? "You" : "Bot"}:</strong> {msg.text}
          </p>
        ))}
      </div>

      <input 
        placeholder="Ask me anything about finance…" 
        value={input}
        onChange={e => setInput(e.target.value)}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
