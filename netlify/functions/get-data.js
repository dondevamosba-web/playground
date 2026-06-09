const { google } = require("googleapis");

const SHEET_ID = process.env.EXPENSE_SHEET_ID;
const SA_JSON  = process.env.GOOGLE_SERVICE_ACCOUNT_JSON;

function getAuth() {
  return new google.auth.GoogleAuth({
    credentials: JSON.parse(SA_JSON),
    scopes: ["https://www.googleapis.com/auth/spreadsheets.readonly"],
  });
}

function currentMonthLabel() {
  const now = new Date();
  return now.toLocaleString("en-US", { month: "short", year: "numeric" });
  // e.g. "May 2026"
}

exports.handler = async (event) => {
  const type = event.queryStringParameters?.type || "month";
  const sheets = google.sheets({ version: "v4", auth: getAuth() });

  if (type === "assets") {
    const res = await sheets.spreadsheets.values.get({
      spreadsheetId: SHEET_ID,
      range: "Assets!A2:D20",
    });
    const rows = (res.data.values || []).map(r => ({
      asset:       r[0] || "",
      value:       r[1] !== "" && r[1] !== undefined ? parseFloat(r[1]) : null,
      notes:       r[2] || "",
      lastUpdated: r[3] || "",
    })).filter(r => r.asset);
    return { statusCode: 200, headers: { "Content-Type": "application/json" }, body: JSON.stringify(rows) };
  }

  if (type === "month") {
    const res = await sheets.spreadsheets.values.get({
      spreadsheetId: SHEET_ID,
      range: "Log!A2:J500",
    });
    const label = currentMonthLabel();
    const rows = (res.data.values || [])
      .filter(r => (r[1] || "").toLowerCase() === label.toLowerCase())
      .map(r => ({
        timestamp:  r[0] || "",
        month:      r[1] || "",
        type:       r[2] || "daily",
        day:        r[3] || "",
        desc:       r[4] || "",
        ars:        r[5] ? parseFloat(r[5]) : null,
        usd:        r[6] ? parseFloat(r[6]) : null,
        category:   r[7] || "",
        payment:    r[8] || "",
        status:     r[9] || "",
      }));
    return { statusCode: 200, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ month: label, rows }) };
  }

  return { statusCode: 400, body: "Unknown type" };
};
