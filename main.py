import time
from scraper import fetch_page, parse_jobs
from storage import save_to_json, save_to_db
from config import SOURCES, JSON_FILE, DB_FILE, CRAWL_DELAY


def run():
    print("=" * 50)
    print(" Job Scraper - Phase 1")
    print("=" * 50)

    total_new = 0

    for source in SOURCES:
        print(f"\n[Scraping] {source['name']}->{source['url']}")

        soup = fetch_page(source["url"])
        if soup is None:
            print(f"[Skip] could not fetch {source['name']}")
            continue
        jobs = parse_jobs(soup, site=source["site"])
        print(f"[Parsed] {len(jobs)} jobs found")

        if not jobs:
            continue
        new_json = save_to_json(jobs, JSON_FILE)
        print(f"[Parsed] {len(jobs)} jobs found")

        if not jobs:
            continue
        new_json = save_to_json(jobs, JSON_FILE)
        new_db = save_to_db(jobs, DB_FILE)
        total_new += new_db

        # Be polite-- don't hammer the server
        time.sleep(CRAWL_DELAY)
    print(f"\n{'=' *50}")
    print(f" Done. {total_new} new jobs saved to DB.")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run()
