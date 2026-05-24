# -----------config.py----------------------------------------------------------
# central places for all settings. Edit here - don't scatter magic values.

SOURCES = [
    {
        "name": "remoteok",
        "url": "https://remoteok.com/api?tag=python",
        "site": "remoteok",
    },
    # Add more sources here as dicts, same structure as above
]

# Keywords to flag interesting jobs (used for filtering/ bonus email alert)
KEYWORDS = ["python", "backend", "django", "fastapi", "remote"]

# Storage
JSON_FILE = "jobs.json"
DB_FILE = "jobs.db"

# Polite crawl delay between requests (seconds)
CRAWL_DELAY = 2.0
