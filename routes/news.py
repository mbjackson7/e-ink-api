from fastapi import APIRouter

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("")
async def news():
    """
    Suggested integrations:
    - NewsAPI (free tier): https://newsapi.org/
    - RSS feeds via feedparser library
    """
    return {
        "articles": [
            {"id": "1", "title": "Chicago approves new transit funding package", "source": "Tribune"},
            {"id": "2", "title": "Lake Michigan water levels stabilize after wet spring", "source": "WGN"},
            {"id": "3", "title": "City council votes on affordable housing expansion", "source": "Block Club"},
            {"id": "4", "title": "Metra schedule changes effective next month", "source": "Metra"},
            {"id": "5", "title": "Local startup raises Series B round", "source": "Crain's"},
        ]
    }
