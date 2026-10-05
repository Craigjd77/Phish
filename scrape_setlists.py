import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re


def extract_responsive_text(element):
    """Prefer desktop label; phish.net nests short/long names in hide* spans."""
    if element is None:
        return ""
    preferred = element.find("span", class_="hideunder768")
    if preferred and preferred.get_text(strip=True):
        return preferred.get_text(strip=True)
    return element.get_text(" ", strip=True)


def normalize_location(location):
    location = re.sub(r"\s+", " ", location or "").strip()
    return re.sub(r"\s*,\s*", ", ", location)


def scrape_setlists(start_year=1983, end_year=datetime.now().year):
    base_url = "https://phish.net/setlists/phish/"
    setlists = []

    for year in range(start_year, end_year + 1):
        url = f"{base_url}?year={year}"
        print(f"Scraping year: {year}")

        try:
            response = requests.get(url, timeout=45)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            setlist_containers = soup.find_all("div", class_="setlist-container")
            print(f"Found {len(setlist_containers)} setlists for year {year}")

            for setlist in setlist_containers:
                date_el = setlist.find("span", class_="setlist-date")
                date = date_el.get_text(" ", strip=True) if date_el else ""
                venue = extract_responsive_text(setlist.find("div", class_="setlist-venue"))
                location = normalize_location(
                    extract_responsive_text(setlist.find("div", class_="setlist-location"))
                )
                body = setlist.find("div", class_="setlist-body")
                setlist_text = body.get_text("\n", strip=True) if body else ""

                setlists.append(
                    {
                        "date": date,
                        "venue": venue,
                        "location": location,
                        "setlist": setlist_text,
                    }
                )

            time.sleep(1)

        except requests.RequestException as e:
            print(f"Error scraping year {year}: {e}")

    return setlists


if __name__ == "__main__":
    start_time = time.time()
    all_setlists = scrape_setlists()
    end_time = time.time()

    print(f"Scraped {len(all_setlists)} setlists in {end_time - start_time:.2f} seconds")

    with open("phish_setlists.json", "w", encoding="utf-8") as file:
        json.dump(all_setlists, file, ensure_ascii=False, indent=4)

    print("Setlists saved to phish_setlists.json")
