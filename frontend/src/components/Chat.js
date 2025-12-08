import React, { useState } from "react";
import { chat } from "../api";

export default function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  async function sendMessage() {
    if (!input.trim()) return;

    setMessages(prev => [...prev, { from: "user", text: input }]);

    const res = await chat(input);

    setMessages(prev => [...prev, { from: "bot", text: res.reply }]);
    setInput("");
  }

  return (
    <div className="chat-box">
      <h2>Chat with FinanceBot</h2>

      <div className="chat-window">
        {messages.map((msg, i) => (
          <p key={i} className={msg.from}>
            <strong>{msg.from}:</strong> {msg.text}
          </p>
        ))}
      </div>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask anything…"
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
