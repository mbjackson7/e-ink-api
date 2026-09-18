from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from playwright.async_api import async_playwright
import httpx
import tempfile
from urllib.parse import urljoin
from utils import get_random_photo_from_folder

router = APIRouter(prefix="/api/media", tags=["media"])


@router.get("/random")
async def media_random(folder: str = "", ratio: float | None = None):
    """
    Randomly return a photo from the specified local folder (all if none specified)
    """
    return await get_random_photo_from_folder(f"./assets/images/{folder}", ratio=ratio)


@router.get("/image-from-page")
async def image_from_page(url: str, click_first: bool = False):
    """
    Uses Playwright to navigate to a URL, find the largest image on the page,
    and return it as a FileResponse.

    Query parameters:
    - url (required): The URL to scrape (URL-encoded)
    - click_first (optional, default=false): If true, clicks the first image on the page,
      waits for load, then finds the largest image
    """
    if not url:
        raise HTTPException(status_code=400, detail="url parameter is required")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=12000)
            await page.wait_for_timeout(4000)

            # If click_first is True, click a random image and wait for load
            if click_first:
                first_img_src = await page.evaluate("""
                    () => {
                        const imgs = Array.from(document.querySelectorAll('img'));
                        if (imgs.length === 0) return null;
                        
                        // Pick a random image
                        const randomImg = imgs[Math.floor(Math.random() * imgs.length)];
                        
                        // Find the <a> element wrapping the image
                        const linkElement = randomImg.closest('a');
                        if (linkElement) {
                            linkElement.click();
                            return randomImg.src;
                        } else {
                            // Fallback: click the image itself if no wrapping <a>
                            randomImg.click();
                            return randomImg.src;
                        }
                    }
                """)

                if not first_img_src:
                    raise HTTPException(
                        status_code=404, detail="No images found on page to click"
                    )

                # Wait for page to load after click (could be navigation or dynamic load)
                await page.wait_for_timeout(2000)
                try:
                    await page.wait_for_load_state("domcontentloaded", timeout=5000)
                except:
                    pass  # In case it's a modal or doesn't navigate

            # Get all images and their dimensions
            images = await page.evaluate("""
                () => {
                    const imgs = Array.from(document.querySelectorAll('img'));
                    return imgs.map(img => ({
                        src: img.src || img.data_src || '',
                        width: img.naturalWidth || img.width || 0,
                        height: img.naturalHeight || img.height || 0,
                        area: (img.naturalWidth || img.width || 0) * (img.naturalHeight || img.height || 0)
                    })).filter(img => img.src && img.area > 0);
                }
            """)

            if not images:
                raise HTTPException(status_code=404, detail="No images found on page")

            # Sort by area and get the largest
            largest = sorted(images, key=lambda x: x["area"], reverse=True)[0]

            # Handle relative URLs
            img_url = largest["src"]
            if img_url.startswith("/"):
                img_url = urljoin(url, img_url)
            elif not img_url.startswith("http"):
                img_url = urljoin(url, img_url)

            # Download the image
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    img_url,
                    follow_redirects=True,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                )
                response.raise_for_status()

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

            await browser.close()

            return FileResponse(
                tmp_path,
                media_type=response.headers.get("content-type", "image/jpeg"),
                headers={"cache-control": "no-cache"},
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")
