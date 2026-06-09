# Friend Follow-up Reminders

## Objective
Keep in touch with friends by tracking when you last messaged them and getting email reminders when it's time to reach out again.

## Sheet Structure
**Google Sheet:** "Friend Follow-ups"

| Column | Description |
|--------|-------------|
| Name | Friend's name |
| Last Contact | Date of last message (YYYY-MM-DD) |
| Frequency (days) | How often to reach out (e.g. 30 = monthly) |
| Notes | What to talk about, context, etc. |

After reaching out, update **Last Contact** to today's date.

## Tool
`tools/friend_followups.py`

## Usage

**Check for overdue friends and create reminder drafts:**
```
python3 tools/friend_followups.py
```

**Preview without creating drafts:**
```
python3 tools/friend_followups.py --dry-run
```

**First-time setup (creates sheet + adds Severiano as example):**
```
python3 tools/friend_followups.py --setup
```

## How it works
1. Reads the sheet
2. For each friend where `today >= Last Contact + Frequency`, flags them as overdue
3. Creates a Gmail draft reminder to `dondevamosba@gmail.com` with the friend's name, notes, and last contact date

## Adding a new friend (manual)
Open the sheet and add a row:
- Name: `Severiano`
- Last Contact: `2025-04-01`
- Frequency (days): `30`
- Notes: `Catch up, check how things are going`

Or ask Claude to add them:
> "Add Marco to the friend tracker, last spoke January, remind me every 45 days"

## Edge cases
- If Last Contact or Frequency are blank/invalid, the row is skipped
- Frequency of 0 or negative is ignored
- After sending a message, update Last Contact in the sheet to reset the timer
