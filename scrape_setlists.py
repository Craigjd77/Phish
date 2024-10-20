import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def scrape_setlists(start_year=1983, end_year=datetime.now().year):
    base_url = "https://phish.net/setlists/phish/"
    setlists = []

    for year in range(start_year, end_year + 1):
        url = f"{base_url}?year={year}"
        print(f"Scraping year: {year}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find and parse each setlist on the page
            setlist_containers = soup.find_all('div', class_='setlist-container')
            print(f"Found {len(setlist_containers)} setlists for year {year}")
            
            for setlist in setlist_containers:
                date = setlist.find('span', class_='setlist-date').text.strip()
                venue = setlist.find('div', class_='setlist-venue').text.strip()
                location = setlist.find('div', class_='setlist-location').text.strip()
                setlist_text = setlist.find('div', class_='setlist-body').text.strip()
                
                setlists.append({
                    'date': date,
                    'venue': venue,
                    'location': location,
                    'setlist': setlist_text
                })
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)
            
        except requests.RequestException as e:
            print(f"Error scraping year {year}: {e}")

    return setlists

# Scrape the setlists
start_time = time.time()
all_setlists = scrape_setlists()
end_time = time.time()

print(f"Scraped {len(all_setlists)} setlists in {end_time - start_time:.2f} seconds")

# Save to JSON
with open('phish_setlists.json', 'w', encoding='utf-8') as file:
    json.dump(all_setlists, file, ensure_ascii=False, indent=4)

print("Setlists saved to phish_setlists.json")