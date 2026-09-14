from datetime import datetime, timedelta
from fastapi import APIRouter

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("")
async def calendar():
    """
    Suggested integrations:
    - Google Calendar API (via google-auth + googleapiclient)
    - Home Assistant calendar integration
    - Any CalDAV source via caldav library
    """
    now = datetime.now()
    return {
        "events": [
            {
                "id": "1",
                "title": "Standup",
                "start": now.replace(hour=9, minute=30).isoformat(),
                "end": now.replace(hour=9, minute=45).isoformat(),
                "allDay": False,
                "calendar": "Work",
            },
            {
                "id": "2",
                "title": "Lunch with Alex",
                "start": now.replace(hour=12, minute=0).isoformat(),
                "end": now.replace(hour=13, minute=0).isoformat(),
                "allDay": False,
                "calendar": "Personal",
            },
            {
                "id": "3",
                "title": "Doctor",
                "start": (now + timedelta(days=1)).replace(hour=10, minute=0).isoformat(),
                "end": (now + timedelta(days=1)).replace(hour=11, minute=0).isoformat(),
                "allDay": False,
                "calendar": "Personal",
            },
        ]
    }
