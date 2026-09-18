from fastapi import APIRouter
from utils import get_ha_state

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("")
async def weather():
    """
    Suggested integrations:
    - Open-Meteo (free, no key): https://open-meteo.com/
    - Home Assistant weather entity via HA REST API
    """
    return {
        "current": {
            "temp": 58,
            "feels_like": 54,
            "condition": "Partly cloudy",
            "humidity": 62,
            "wind_speed": 11,
        },
        "forecast": [
            {
                "date": "Mon",
                "high": 61,
                "low": 44,
                "condition": "Sunny",
                "precip_chance": 5,
            },
            {
                "date": "Tue",
                "high": 55,
                "low": 41,
                "condition": "Cloudy",
                "precip_chance": 30,
            },
            {
                "date": "Wed",
                "high": 49,
                "low": 38,
                "condition": "Rain",
                "precip_chance": 80,
            },
            {
                "date": "Thu",
                "high": 52,
                "low": 40,
                "condition": "Partly cloudy",
                "precip_chance": 20,
            },
            {
                "date": "Fri",
                "high": 60,
                "low": 43,
                "condition": "Sunny",
                "precip_chance": 5,
            },
        ],
    }


@router.get("/ha")
async def weather_ha():
    """
    Home Assistant weather entity via HA REST API
    Only contains current conditions
    """
    ENTITY_ID = "weather.openweathermap"
    data = await get_ha_state(ENTITY_ID)
    return {
        "current": {
            "temp": data["attributes"]["temperature"],
            "feels_like": data["attributes"].get(
                "apparent_temperature", data["attributes"]["temperature"]
            ),
            "condition": data["state"].title(),
            "humidity": data["attributes"]["humidity"],
            "wind_speed": data["attributes"]["wind_speed"],
        },
    }
