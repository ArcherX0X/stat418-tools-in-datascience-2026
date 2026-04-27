import json
import logging
import os
import time
from typing import Dict, List
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="logs/web_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

IMDB_BASE = "https://www.imdb.com"
USER_AGENT = "UCLA STAT418 Student - zachwang2015@gmail.com"


def check_robots_txt(url: str = IMDB_BASE) -> bool:
    """Return True if /title/ paths are allowed for our user-agent."""
    robots_url = urljoin(url, "/robots.txt")
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        allowed = rp.can_fetch(USER_AGENT, urljoin(url, "/title/tt0000001/"))
        logger.info("robots.txt check -> can_fetch=%s", allowed)
        return allowed
    except Exception as e:
        logger.warning("Could not read robots.txt: %s", e)
        return False


class IMDbScraper:
    """
    Attempts direct IMDb HTML scraping but falls back to the OMDb API.

    IMDb now protects title pages with AWS WAF (returns HTTP 202 with a
    JS-challenge page), making BeautifulSoup-only scraping unreliable.
    The OMDb API provides the same fields (IMDb rating, vote count,
    Metascore) indexed by IMDb ID and is used as the authoritative source.
    The scraping infrastructure below is retained to demonstrate correct
    web-scraping practice (robots.txt, rate limiting, error handling).
    """

    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.omdb_key = os.getenv("OMDB_API_KEY")
        if not self.omdb_key:
            raise ValueError("OMDB_API_KEY not found in environment")

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
        })
        self._last_request = 0.0

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request = time.time()

    def _scrape_imdb_page(self, imdb_id: str) -> Dict:
        """Try direct HTML scraping of an IMDb title page."""
        self._rate_limit()
        url = f"{IMDB_BASE}/title/{imdb_id}/"
        try:
            resp = self.session.get(url, timeout=10)
            # IMDb returns 202 + JS challenge when WAF is triggered
            if resp.status_code == 202 or len(resp.text) < 5000:
                logger.warning("IMDb WAF challenge for %s (status %d)", imdb_id, resp.status_code)
                return {}
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "lxml")

            # Try JSON-LD structured data first (most reliable when available)
            ld_tag = soup.find("script", type="application/ld+json")
            if ld_tag:
                ld = json.loads(ld_tag.string)
                agg = ld.get("aggregateRating", {})
                return {
                    "imdb_id": imdb_id,
                    "imdb_rating": float(agg.get("ratingValue", 0)) or None,
                    "imdb_votes": int(str(agg.get("ratingCount", "0")).replace(",", "")) or None,
                    "metascore": None,
                    "source": "imdb_scrape",
                }

            # Fallback: CSS selectors for rating elements
            rating_tag = soup.find("span", {"data-testid": "hero-rating-bar__aggregate-rating__score"})
            rating = float(rating_tag.find("span").text) if rating_tag else None

            meta_tag = soup.find("span", {"data-testid": "score-meta"})
            metascore = int(meta_tag.text.strip()) if meta_tag else None

            logger.info("Scraped IMDb page for %s", imdb_id)
            return {
                "imdb_id": imdb_id,
                "imdb_rating": rating,
                "imdb_votes": None,
                "metascore": metascore,
                "source": "imdb_scrape",
            }
        except Exception as e:
            logger.error("Scrape failed for %s: %s", imdb_id, e)
            return {}

    def _fetch_omdb(self, imdb_id: str) -> Dict:
        """Fetch rating data from OMDb API using IMDb ID."""
        self._rate_limit()
        try:
            resp = requests.get(
                "http://www.omdbapi.com/",
                params={"i": imdb_id, "apikey": self.omdb_key},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("Response") != "True":
                logger.warning("OMDb returned no result for %s: %s", imdb_id, data.get("Error"))
                return {"imdb_id": imdb_id, "imdb_rating": None, "imdb_votes": None, "metascore": None, "source": "omdb"}

            def parse_num(val: str):
                if not val or val == "N/A":
                    return None
                return float(val.replace(",", ""))

            logger.info("OMDb fetched %s", imdb_id)
            return {
                "imdb_id": imdb_id,
                "imdb_rating": parse_num(data.get("imdbRating")),
                "imdb_votes": int(parse_num(data.get("imdbVotes")) or 0) or None,
                "metascore": int(parse_num(data.get("Metascore")) or 0) or None,
                "source": "omdb",
            }
        except Exception as e:
            logger.error("OMDb error for %s: %s", imdb_id, e)
            return {"imdb_id": imdb_id, "imdb_rating": None, "imdb_votes": None, "metascore": None, "source": "omdb"}

    def scrape_movie_page(self, imdb_id: str) -> Dict:
        """Return IMDb rating data, trying direct scrape then OMDb fallback."""
        if not imdb_id:
            return {"imdb_id": imdb_id, "imdb_rating": None, "imdb_votes": None, "metascore": None, "source": "none"}
        result = self._scrape_imdb_page(imdb_id)
        if not result or result.get("imdb_rating") is None:
            result = self._fetch_omdb(imdb_id)
        return result

    def scrape_multiple_movies(self, imdb_ids: List[str]) -> List[Dict]:
        """Scrape rating data for a list of IMDb IDs."""
        results = []
        for i, imdb_id in enumerate(imdb_ids, 1):
            print(f"  [{i}/{len(imdb_ids)}] {imdb_id}")
            results.append(self.scrape_movie_page(imdb_id))
        return results


def save_raw_data(data: List[Dict], output_dir: str = "data/raw/imdb") -> None:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "ratings.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved %d records to %s", len(data), path)
    print(f"Saved {len(data)} records to {path}")


def main(imdb_ids: List[str] = None) -> List[Dict]:
    os.makedirs("logs", exist_ok=True)

    robots_ok = check_robots_txt()
    print(f"IMDb robots.txt allows scraping /title/ paths: {robots_ok}")

    if imdb_ids is None:
        import json as _json
        with open("data/raw/tmdb/movies.json") as f:
            tmdb_data = _json.load(f)
        imdb_ids = [m["imdb_id"] for m in tmdb_data if m.get("imdb_id")]

    scraper = IMDbScraper(delay=2.0)
    print(f"Fetching rating data for {len(imdb_ids)} movies...")
    results = scraper.scrape_multiple_movies(imdb_ids)
    save_raw_data(results)
    return results


if __name__ == "__main__":
    main()
