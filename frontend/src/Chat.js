import React, { useState } from "react";
import { chatWithBot } from "./api/api";

function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hi 👋 I’m NiveshBuddy. Ask me about SIPs, EMIs, or mutual funds.",
    },
  ]);
  const [loading, setLoading] = useState(false);

  const quickQuestions = [
    "What is SIP?",
    "Calculate EMI for 10 lakh at 9% for 15 years",
    "My income is 50k. How much SIP should I do?",
    "Tell me about index funds",
  ];

  const sendMessage = async (msg) => {
    const messageToSend = msg || input;
    if (!messageToSend.trim()) return;

    setMessages((prev) => [...prev, { sender: "user", text: messageToSend }]);
    setInput("");
    setLoading(true);

    try {
      const reply = await chatWithBot(messageToSend);
      setMessages((prev) => [...prev, { sender: "bot", text: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-wrapper">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`message ${msg.sender === "user" ? "user-msg" : "bot-msg"}`}
          >
            {msg.text}
          </div>
        ))}

        {loading && <div className="bot-msg typing">Typing…</div>}
      </div>

      <div className="quick-actions">
        {quickQuestions.map((q, i) => (
          <button key={i} onClick={() => sendMessage(q)}>
            {q}
          </button>
        ))}
      </div>

      <div className="input-row">
        <input
          type="text"
          placeholder="Ask about SIP, EMI, mutual funds…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={() => sendMessage()}>Send</button>
      </div>
    </div>
  );
}

export default Chat;
