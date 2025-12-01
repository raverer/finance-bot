import React, { useState } from "react";
import { chat } from "./api/api";

function App() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  async function handleSend() {
    const res = await chat(message);
    setResponse(res.response || "");
  }

  return (
    <div style={{ padding: "40px", maxWidth: "600px", margin: "0 auto" }}>
      <h1>Finance Bot</h1>

      <textarea
        rows="3"
        style={{ width: "100%", padding: "10px" }}
        placeholder="Ask something..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />

      <button
        onClick={handleSend}
        style={{ marginTop: "10px", padding: "10px 20px" }}
      >
        Send
      </button>

      {response && (
        <div style={{ marginTop: "20px", padding: "15px", background: "#eee" }}>
          <strong>Bot Reply:</strong>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}

export default App;
