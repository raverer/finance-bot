const BASE_URL = "https://web-production-79d0d.up.railway.app/";

export async function chat(message) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  return res.json();
}

export async function calculateEMI(data) {
  const res = await fetch(`${BASE_URL}/emi/calc`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function calculateSIP(data) {
  const res = await fetch(`${BASE_URL}/sip/calc-name`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}
