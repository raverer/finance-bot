// frontend/src/api/api.js

// Railway backend base URL
const API_BASE = "https://web-production-79d0d.up.railway.app";

// ================= CHAT API =================
export async function chatWithBot(message) {
  try {
    const res = await fetch(`${API_BASE}/chat`, { 
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) return "Server error. Please try again.";

    const data = await res.json();
    return data.reply;
  } catch (err) {
    console.error("Chat error:", err);
    return "Network error. Please try again.";
  }
}

// ================= EMI API =================
export async function calculateEMI(data) {
  try {
    const res = await fetch(`${API_BASE}/emi/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    return await res.json();
  } catch (err) {
    console.error("EMI error:", err);
    return { error: "Unable to calculate EMI" };
  }
}

// ================= SIP API =================
export async function calculateSIP(data) {
  try {
    const res = await fetch(`${API_BASE}/sip/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    return await res.json();
  } catch (err) {
    console.error("SIP error:", err);
    return { error: "Unable to calculate SIP" };
  }
}
