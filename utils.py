import os
import random

import cv2
from fastapi import HTTPException
from fastapi.responses import FileResponse
import httpx


async def get_ha_state(entity_id: str = "") -> dict:
    """Fetch Home Assistant entity state"""
    HA_URL = os.environ.get('HA_URL', 'http://homeassistant.local:8123')
    HA_TOKEN = os.environ["HA_ACCESS_TOKEN"]
    headers = {"Authorization": f"Bearer {HA_TOKEN}"}
    print(f"Fetching HA state for {entity_id} from {HA_URL} with token {HA_TOKEN[:8]}...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{HA_URL}/api/states/{entity_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    

ratio_cache = {}

def get_ratio_from_path(photo_path: str) -> float:
    if photo_path in ratio_cache:
        return ratio_cache[photo_path]
    if photo_path.endswith('.mp4') or photo_path.endswith('.avi'):
        # For videos, get ratio of the first frame
        cap = cv2.VideoCapture(photo_path)
        ret, img = cap.read()
        cap.release()
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to read video frame for ratio calculation")
    else:
        img = cv2.imread(photo_path)
    h, w = img.shape[:2]
    ratio = w / h
    ratio_cache[photo_path] = ratio
    return ratio

async def get_random_photo_from_folder(folder_path: str, ratio: float | None = None, ratio_tolerance: float = 0.1) -> FileResponse:
    """Return a random photo from a folder or its subdirectories
    
    If ratio is provided, only return photos with width/height close to that ratio (e.g. 16/9 = 1.77)
    """
    photos = []
    print(f"Searching for photos in {folder_path}...")
    # Recursively search for image files
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if f.endswith(('.png', '.jpg', '.jpeg', '.webp', '.mp4', '.avi')):
                photos.append(os.path.join(root, f))

    print(f"Found {len(photos)} photos in {folder_path}")
    
    if not photos:
        raise HTTPException(status_code=404, detail="No photos found")
    
    if ratio is not None:
        # Compute ratio diff for every photo once, store as (diff, path)
        scored = []
        for p in photos:
            try:
                photo_ratio = get_ratio_from_path(p)
                diff = abs(photo_ratio - ratio)
                scored.append((diff, p))
            except:
                pass

        # Sort by diff so the 10 closest are simply the first 10
        scored.sort(key=lambda x: x[0])

        in_tolerance = [p for diff, p in scored if diff < ratio_tolerance]
        photos = in_tolerance if len(in_tolerance) >= 10 else [p for _, p in scored[:10]]

    selected_photo = random.choice(photos)
    
    # Determine media type based on file extension
    if selected_photo.endswith('.webp'):
        media_type = 'image/webp'
    elif selected_photo.endswith(('.jpg', '.jpeg')):
        media_type = 'image/jpeg'
    elif selected_photo.endswith('.png'):
        media_type = 'image/png'
    else:
        return extract_random_frame(selected_photo)
        
    return FileResponse(
        selected_photo, 
        media_type=media_type, 
        headers={"cache-control": "no-cache"}
    )


def extract_random_frame(video_path: str) -> FileResponse:
    cap = cv2.VideoCapture(video_path)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    random_frame = random.randint(0, total_frames - 1)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
    ret, frame = cap.read()
    
    if not ret:
        raise HTTPException(status_code=500, detail="Failed to read video frame")
    
    # Save frame to temporary file
    temp_path = f"/tmp/frame_{random_frame}.jpg"
    cv2.imwrite(temp_path, frame)
    cap.release()
    return FileResponse(
        temp_path,
        media_type="image/jpeg",
        headers={"cache-control": "no-cache"}
    )