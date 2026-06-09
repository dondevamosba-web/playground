const { google } = require("googleapis");

const SHEET_ID  = process.env.EXPENSE_SHEET_ID;
const SA_JSON   = process.env.GOOGLE_SERVICE_ACCOUNT_JSON;
const SHEET_TAB = "Log";

function getAuth() {
  const creds = JSON.parse(SA_JSON);
  return new google.auth.GoogleAuth({
    credentials: creds,
    scopes: ["https://www.googleapis.com/auth/spreadsheets"],
  });
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  let p;
  const ct = event.headers["content-type"] || "";
  if (ct.includes("application/json")) {
    p = JSON.parse(event.body || "{}");
  } else {
    const params = new URLSearchParams(event.body || "");
    p = Object.fromEntries(params.entries());
  }

  if (p["bot-field"]) {
    return { statusCode: 200, body: JSON.stringify({ ok: true }) };
  }

  if (!p.month || !p.description) {
    return { statusCode: 400, body: JSON.stringify({ error: "Missing month or description" }) };
  }

  const row = [
    new Date().toISOString(),
    p.month        || "",
    p.entry_type   || "daily",
    p.day          || "",
    p.description  || "",
    p.ars          ? parseFloat(p.ars)  : "",
    p.usd          ? parseFloat(p.usd)  : "",
    p.category     || "",
    p.payment      || "",
    p.status       || "",
  ];

  const auth   = getAuth();
  const sheets = google.sheets({ version: "v4", auth });

  await sheets.spreadsheets.values.append({
    spreadsheetId: SHEET_ID,
    range: `${SHEET_TAB}!A:J`,
    valueInputOption: "USER_ENTERED",
    insertDataOption: "INSERT_ROWS",
    requestBody: { values: [row] },
  });

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ok: true }),
  };
};
