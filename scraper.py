import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
def fetch_page(url: str, retries: int = 3, delay: float = 1.5) -> BeautifulSoup | None:
    """Fetch a URL and return a BeautifulSoup object. Retries on failure"""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.HTTPError as e:
            print(f"[HTTP Error] {e} - attempt {attempt}/{retries}")
        except requests.exceptions.ConnectionError:
            print(f"[Connection Error] could not reach {url} -attempt {attempt}/{retries}")
        except requests.exceptions.Timeout:
            print(f"[Timeout] Request timed out - attempt {attempt}/{retries}")
        if attempt < retries:
            time.sleep(delay)
    print(f"[Failed] Could not fetch: {url}")
    return None
def parse_jobs(soup: BeautifulSoup, site: str = "default")-> list[dict]:
    """Parse job listings from a BeautifulSoup Object
    Each site has a different HTML structure - add a new parser per site.
    Returns a list of job dicts:{ title, company, location, url}"""
    parsers = {
        "remoteok": _parse_remoteok,
        "default": _parse_default,
    }
    parser = parsers.get(site, parsers["default"])
    jobs = []

    try:
        jobs = parser(soup)
    except Exception as e:
        print(f"[Parse Error] Failed to parse jobs for site='{site}': {e}")
    return jobs
#--------Site specific parsers-----------------------------------------------
def _parse_remoteok(soup: BeautifulSoup) -> list[dict]:
    """Parser for remoteok.com - update selectors if the site changes."""
    jobs = []
    for row in soup.select("tr.job"):
        try:
            jobs.append({
                "title": row.select_one("h2[itemprop='title']").get_text(strip=True),
                "company": row.select_one("h3[itemprop='name']").get_text(strip=True),
                "location": row.select_one("div.location").get_text(strip=True) if row.select_one("div.location") else "Remote",
                "url": "https://remoteok.com" + row.get("data-href", ""),
                "tags": [t.get_text(strip=True) for t in row.select("a.tag")],
            })
        except AttributeError:
            continue   #Skip malformed rows
    return jobs
def _parse_default(soup: BeautifulSoup) -> list[dict]:
    """
    Generic fallback parser - replace selectors for your target site.
    Inspect the page with browser DevTools to find the right selectors."""

    jobs = []
    for card in soup.select("div.job-card"):               #<- update selector
        try:
            jobs.append({
                "title": card.select_one("h2. title").get_text(strip=True),
                "company": card.select_one("span.company").get_text(Strip=True),
                "location": card.select_one("span.location").get_text(Strip=True),
                "url":      card.select_one("a")["href"],
                "tags":    [],
            })
        except AttributeError:
            continue
    return jobs
