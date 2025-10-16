import datetime as dt
import os
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _get_service():
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials/service_account.json")
    credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
    return service


def get_upcoming_events(days: int = 7, max_results: int = 10) -> str:
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "")
    if not calendar_id:
        return "Google Calendar ID is not configured."

    service = _get_service()
    now = dt.datetime.utcnow().isoformat() + "Z"
    end_time = (dt.datetime.utcnow() + dt.timedelta(days=days)).isoformat() + "Z"

    events_result = (
        service.events()
        .list(calendarId=calendar_id, timeMin=now, timeMax=end_time, singleEvents=True, orderBy="startTime", maxResults=max_results)
        .execute()
    )
    events: List[dict] = events_result.get("items", [])
    if not events:
        return "No upcoming events found."

    lines: List[str] = []
    for ev in events:
        start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date")
        summary = ev.get("summary", "(no title)")
        location = ev.get("location")
        start_fmt = start
        try:
            if "T" in start:
                start_dt = dt.datetime.fromisoformat(start.replace("Z", "+00:00"))
                start_fmt = start_dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
        if location:
            lines.append(f"- {start_fmt}: {summary} @ {location}")
        else:
            lines.append(f"- {start_fmt}: {summary}")
    return "Upcoming events:\n" + "\n".join(lines)
