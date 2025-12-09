import React, { useState } from "react";
import { chatWithBot } from "./api/api";

function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);

    console.log("📤 Sending to API:", input);

    try {
      const botReply = await chatWithBot(input);

      console.log("📥 API Response:", botReply);

      if (!botReply) {
        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: "Server returned empty response." },
        ]);
        return;
      }

      const botMessage = { sender: "bot", text: botReply };
      setMessages((prev) => [...prev, botMessage]);

    } catch (err) {
      console.error("❌ API Error:", err);

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error contacting server. Check console logs." },
      ]);
    }

    setInput("");
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.sender === "user" ? "user-msg" : "bot-msg"}`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="input-row">
        <input
          type="text"
          placeholder="Ask me anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chat;
