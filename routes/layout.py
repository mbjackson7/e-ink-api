import json
import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/layout", tags=["layout"])

LAYOUTS_DIR = os.environ.get(
    'LAYOUTS_DIR',
    os.path.join(os.path.dirname(__file__), '..', 'layouts')
)


def build_layout_response(widgets):
    """
    Converts flat widget list into the shape the client expects:
    {
      widgets: [ { id, type, title, config } ],
      layouts: { lg: [...], md: [...], sm: [...] }
    }
    """
    layout_items = {"lg": [], "md": [], "sm": []}
    widget_meta = []

    for w in widgets:
        widget_meta.append({
            "id": w["id"],
            "type": w["type"],
            "title": w["title"],
            "config": w.get("config", {}),
        })
        for bp in layout_items:
            layout_items[bp].append({
                "i": w["id"],
                "minW": 2,
                "minH": 1,
                **w[bp],
            })

    return {"widgets": widget_meta, "layouts": layout_items}


@router.get("")
async def get_layout(name: str = "default"):
    """
    Returns widget metadata + layout positions.
    Uses layout.json if it exists, otherwise DEFAULT_WIDGETS.
    """
    LAYOUT_PATH = os.path.join(LAYOUTS_DIR, f"{name}.json")
    if os.path.exists(LAYOUT_PATH):
        with open(LAYOUT_PATH) as f:
            return json.load(f)
    
    # Return empty layout if no file exists
    return {"widgets": [], "layouts": {"lg": [], "md": [], "sm": []}}

@router.get("/list")
async def list_layouts():
    """
    Returns a list of available layout files.
    """
    return {
        "layouts": [
            f[:-5] for f in os.listdir(LAYOUTS_DIR) if f.endswith(".json") and not f.startswith(".")
        ]
    }

@router.post("")
async def save_layout(body: dict, name: str = "default"):
    """
    Persists the full layout response shape to layout.json.
    Body: { widgets: [...], layouts: { lg, md, sm } }
    name: layout name, used as filename (default "default")
    """
    LAYOUT_PATH = os.path.join(LAYOUTS_DIR, f"{name}.json")
    try:
        with open(LAYOUT_PATH, 'w') as f:
            json.dump(body, f, indent=2)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
