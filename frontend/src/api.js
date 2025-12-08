export const API_BASE = "https://web-production-79d0d.up.railway.app";

export async function chat(query) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  });
  return response.json();
}

export async function calculateEmi(data) {
  const response = await fetch(`${API_BASE}/emi/single`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return response.json();
}

export async function calculateSip(data) {
  const response = await fetch(`${API_BASE}/sip/calc`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return response.json();
}
