const { google } = require("googleapis");

const SHEET_ID = process.env.LEADS_SHEET_ID;
const SA_JSON  = process.env.GOOGLE_SERVICE_ACCOUNT_JSON;

function getAuth() {
  return new google.auth.GoogleAuth({
    credentials: JSON.parse(SA_JSON),
    scopes: ["https://www.googleapis.com/auth/spreadsheets"],
  });
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  const params = new URLSearchParams(event.body || "");
  const p = Object.fromEntries(params.entries());

  // Honeypot
  if (p["bot-field"]) {
    return { statusCode: 200, body: JSON.stringify({ ok: true }) };
  }

  if (!p.email) {
    return { statusCode: 400, body: JSON.stringify({ error: "Email required" }) };
  }

  const row = [
    new Date().toISOString(),
    p.nombre   || "",
    p.email    || "",
    p.negocio  || "",
    p.telefono || "",
    p.servicio || "",
    p.mensaje  || "",
  ];

  const auth = getAuth();
  const sheets = google.sheets({ version: "v4", auth });
  await sheets.spreadsheets.values.append({
    spreadsheetId: SHEET_ID,
    range: "A1",
    valueInputOption: "RAW",
    insertDataOption: "INSERT_ROWS",
    requestBody: { values: [row] },
  });

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ok: true }),
  };
};
