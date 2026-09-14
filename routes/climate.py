from fastapi import APIRouter
from utils import get_ha_state

router = APIRouter(prefix="/api/climate", tags=["climate"])


@router.get("")
async def climate():
    """
    Suggested integration:
    - Home Assistant REST API: GET /api/states/<entity_id>
    - Example entity IDs: sensor.living_room_temperature, sensor.living_room_humidity
    """
    return {
        "fields": {
            "temperature": {"value": 70, "unit": "°F"},
            "humidity": {"value": 48, "unit": "%"},
        }
    }


@router.get("/ha")
async def climate_ha():
    """
    Home Assistant climate entity via HA REST API
    """
    ENTITY_ID = "climate.sensi_161c21_thermostat"
    data = await get_ha_state(ENTITY_ID)
    return {
        "fields": {
            "temperature": {"value": data["attributes"]["current_temperature"], "unit": "°F"},
            "humidity": {"value": data["attributes"].get("humidity"), "unit": "%"},
            "state": {"value": data["state"], "unit": ""},
        }
    }
