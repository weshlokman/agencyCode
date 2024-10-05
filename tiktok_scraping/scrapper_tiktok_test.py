import asyncio
import json
import sqlite3
from typing import List, Dict
from httpx import AsyncClient, Response
from parsel import Selector
from loguru import logger as log
import brotli

# initialize an async httpx client
client = AsyncClient(
    # enable http2
    http2=True,
    # add basic browser like headers to prevent being blocked
    headers={
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
    },
)

import brotli  # Add this import


def parse_profile(response: Response):
    """Parse profile data from hidden scripts on the HTML"""
    assert response.status_code == 200, "Request is blocked or failed"

    encoding = response.headers.get("Content-Encoding", "")
    try:
        if encoding == "br":
            log.debug("Response is Brotli encoded, attempting to decode.")
            # Skip Brotli decompression if it fails, as it might not be correctly encoded
            try:
                response_text = brotli.decompress(response.content).decode('utf-8', errors='replace')
            except brotli.error:
                log.error("Brotli decompression failed, treating as plain text.")
                response_text = response.text
        else:
            response_text = response.text
    except Exception as e:
        log.error(f"Failed to decode response: {e}")
        return None

    selector = Selector(response_text)

    # Try to extract the data
    data = selector.xpath("//script[@id='__UNIVERSAL_DATA_FOR_REHYDRATION__']/text()").get()

    if data is None:
        log.error("No data found in the response. Verify the XPath expression or HTML structure.")
        log.debug(f"Response text: {response_text[:500]}")
        return None

    try:
        profile_data = json.loads(data)["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]
        return profile_data
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        log.error(f"Failed to parse profile data: {e}")
        log.debug(f"Data content: {data}")
        return None


async def scrape_profiles(urls: List[str]) -> List[Dict]:
    """scrape tiktok profiles data from their URLs"""
    to_scrape = [client.get(url) for url in urls]
    data = []
    # scrape the URLs concurrently
    for response in asyncio.as_completed(to_scrape):
        response = await response
        profile_data = parse_profile(response)
        data.append(profile_data)
    log.success(f"scraped {len(data)} profiles from profile pages")
    return data


async def main():
    # Connect to the SQLite database
    conn = sqlite3.connect("tiktok_videos.db")
    cursor = conn.cursor()

    # Get profile links from the database
    cursor.execute("SELECT profile_link FROM tiktok_videos_1")
    profile_links = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Extract profile links from the fetched data
    links = [link[0] for link in profile_links if link[0]]  # Filter out None values

    # Run scraping for all profile links
    await asyncio.gather(*(scrape_profiles(link) for link in links))



if __name__ == "__main__":
    asyncio.run(main())
