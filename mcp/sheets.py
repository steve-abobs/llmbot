import os
import datetime as dt
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def _get_service():
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials/service_account.json")
    credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    return service


def get_homework_for_today() -> str:
    sheet_id = os.getenv("GOOGLE_SHEETS_ID", "")
    if not sheet_id:
        return "Google Sheets ID is not configured."

    service = _get_service()
    # Convention: first sheet, columns: Date | Subject | Task
    rng = "Sheet1!A:C"
    values = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=rng)
        .execute()
        .get("values", [])
    )

    if not values:
        return "No homework data found."

    today = dt.date.today().isoformat()
    rows: List[str] = []
    for row in values[1:] if values and len(values) > 1 else []:
        date = row[0] if len(row) > 0 else ""
        subject = row[1] if len(row) > 1 else ""
        task = row[2] if len(row) > 2 else ""
        if date == today:
            rows.append(f"- {subject}: {task}")

    if not rows:
        return "No homework for today."
    return "Homework for today:\n" + "\n".join(rows)
