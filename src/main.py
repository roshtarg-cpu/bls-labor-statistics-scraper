"""
BLS Labor Statistics Scraper — Main actor logic
Fetches time-series data from the Bureau of Labor Statistics public API
"""
import asyncio
import json
import logging
from datetime import datetime, timezone

import httpx
from apify import Actor

logger = logging.getLogger(__name__)

# BLS API base URL
BLS_API_V2 = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
BLS_API_V1 = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

# Well-known series titles for common IDs
KNOWN_SERIES_TITLES = {
    "CUUR0000SA0": "Consumer Price Index - All Urban Consumers (CPI-U)",
    "CUSR0000SA0": "Consumer Price Index - Urban Wage Earners (CPI-W)",
    "LNS14000000": "Unemployment Rate (Seasonally Adjusted)",
    "CES0000000001": "Total Nonfarm Payroll Employment",
    "CES0500000003": "Average Hourly Earnings - Private Sector",
    "CES0500000008": "Average Weekly Hours - Private Sector",
    "LNS11000000": "Civilian Labor Force",
    "LNS12000000": "Employed Civilians",
    "LNS13000000": "Unemployed Civilians",
    "WPUFD4": "Producer Price Index - Final Demand",
    "EEU00500006": "Average Weekly Earnings - Private Sector",
}


async def fetch_series(client: httpx.AsyncClient, series_ids: list, start_year: int, end_year: int,
                       registration_key: str = None, max_results: int = 50) -> list:
    """
    Fetch BLS time series data for given series IDs.
    Uses v2 API with registration key if available, otherwise v1.
    """
    results = []

    # BLS v2 allows up to 50 series per request with a key; v1 allows 25 without
    batch_size = 50 if registration_key else 25

    for i in range(0, len(series_ids), batch_size):
        batch = series_ids[i:i + batch_size]
        payload = {
            "seriesid": batch,
            "startyear": str(start_year),
            "endyear": str(end_year),
            "calculations": False,
            "annualaverage": False
        }
        if registration_key:
            payload["registrationkey"] = registration_key

        api_url = BLS_API_V2 if registration_key else BLS_API_V1

        for attempt in range(3):
            try:
                logger.info(f"Fetching BLS series batch {i // batch_size + 1}: {batch}")
                response = await client.post(
                    api_url,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                if data.get("status") != "REQUEST_SUCCEEDED":
                    messages = data.get("message", [])
                    logger.warning(f"BLS API status: {data.get('status')}, messages: {messages}")
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue

                for series in data.get("Results", {}).get("series", []):
                    series_id = series.get("seriesID", "")
                    series_data = series.get("data", [])
                    title = KNOWN_SERIES_TITLES.get(series_id, series_id)

                    count = 0
                    for point in series_data:
                        if count >= max_results:
                            break
                        footnotes_list = point.get("footnotes", [])
                        footnote_texts = [f.get("text", "") for f in footnotes_list if f.get("text")]
                        
                        results.append({
                            "seriesId": series_id,
                            "seriesTitle": title,
                            "year": point.get("year"),
                            "period": point.get("period"),
                            "periodName": point.get("periodName"),
                            "value": point.get("value"),
                            "latest": point.get("latest", False),
                            "footnotes": "; ".join(footnote_texts) if footnote_texts else None,
                            "scrapedAt": datetime.now(timezone.utc).isoformat()
                        })
                        count += 1

                break  # Success - exit retry loop

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)

    return results


async def main():
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}

        series_ids = actor_input.get("seriesIds", ["CUUR0000SA0", "LNS14000000", "CES0000000001"])
        start_year = actor_input.get("startYear", 2020)
        end_year = actor_input.get("endYear", 2024)
        registration_key = actor_input.get("registrationKey", "") or None
        max_results = actor_input.get("maxResults", 50)

        # Validate inputs
        if not series_ids:
            logger.warning("No series IDs provided, using defaults")
            series_ids = ["CUUR0000SA0", "LNS14000000", "CES0000000001"]

        if not isinstance(series_ids, list):
            series_ids = [series_ids]

        # Clamp years
        current_year = datetime.now(timezone.utc).year
        start_year = max(1913, min(start_year, current_year))
        end_year = max(start_year, min(end_year, current_year))

        logger.info(f"Fetching BLS data for {len(series_ids)} series: {series_ids}")
        logger.info(f"Year range: {start_year}-{end_year}, maxResults per series: {max_results}")

        async with httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "User-Agent": "ApifyActor/BLSScraper apify.com/fervent_bus/bls-labor-statistics-scraper"
            },
            follow_redirects=True
        ) as client:
            results = await fetch_series(
                client,
                series_ids,
                start_year,
                end_year,
                registration_key=registration_key,
                max_results=max_results
            )

        # Push results to dataset
        total = 0
        for item in results:
            await Actor.push_data(item)
            total += 1
            if total % 10 == 0:
                logger.info(f"Progress: {total} data points pushed")

        logger.info(f"Done! Total data points scraped: {total}")

        if total == 0:
            logger.warning("No data points were scraped. Check series IDs and year range.")
