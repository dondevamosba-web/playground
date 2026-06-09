const { google } = require("googleapis");

const SHEET_ID = process.env.EXPENSE_SHEET_ID;
const SA_JSON  = process.env.GOOGLE_SERVICE_ACCOUNT_JSON;

function getAuth() {
  return new google.auth.GoogleAuth({
    credentials: JSON.parse(SA_JSON),
    scopes: ["https://www.googleapis.com/auth/spreadsheets"],
  });
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") return { statusCode: 405 };

  const { asset, operation, amount } = JSON.parse(event.body || "{}");
  if (!asset || !operation || amount == null) {
    return { statusCode: 400, body: "Missing asset, operation, or amount" };
  }

  const sheets = google.sheets({ version: "v4", auth: getAuth() });

  // Read current assets to find the row
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId: SHEET_ID,
    range: "Assets!A2:D20",
  });
  const rows = res.data.values || [];
  const rowIdx = rows.findIndex(r => r[0] === asset);
  if (rowIdx === -1) return { statusCode: 404, body: "Asset not found" };

  const current = parseFloat(rows[rowIdx][1]) || 0;
  const delta   = parseFloat(amount);
  const newVal  = operation === "add" ? current + delta : current - delta;
  const sheetRow = rowIdx + 2; // 1-indexed + header row

  await sheets.spreadsheets.values.update({
    spreadsheetId: SHEET_ID,
    range: `Assets!B${sheetRow}:D${sheetRow}`,
    valueInputOption: "USER_ENTERED",
    requestBody: {
      values: [[newVal, rows[rowIdx][2] || "", new Date().toISOString().split("T")[0]]],
    },
  });

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ok: true, asset, newVal }),
  };
};
