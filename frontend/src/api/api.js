// frontend/src/api/api.js

const API_BASE = "https://your-railway-backend-url"; 
// Replace with actual Railway URL

// 🟢 Chat
export async function chatWithBot(message) {
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    const data = await res.json();
    return data.response;
  } catch (err) {
    console.error("Chat error:", err);
    return "Something went wrong.";
  }
}

// 🟢 EMI Calculator
export async function calculateEMI(data) {
  const res = await fetch(`${API_BASE}/emi/calculate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return await res.json();
}

// 🟢 SIP Calculator
export async function calculateSIP(data) {
  const res = await fetch(`${API_BASE}/sip/calculate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return await res.json();
}
