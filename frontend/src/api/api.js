// frontend/src/api/api.js

// ✅ IMPORTANT: Use full Railway URL with https://
const API_BASE = "https://web-production-79d0d.up.railway.app";

// ================= CHAT API =================
export async function chatWithBot(message) {
  try {
    const res = await fetch(`${API_BASE}/chat/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    const data = await res.json();

    // Backend returns: { reply: "..." }
    return data.reply;
  } catch (err) {
    console.error("Chat error:", err);
    return "Something went wrong.";
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
