import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def extract_location_data(location_element):
    if location_element:
        location_parts = location_element.get_text(strip=True).split(',')
        if len(location_parts) >= 3:
            voivodeship = location_parts[-3].strip()
            county = location_parts[-2].strip()
            district = location_parts[-1].strip()
            return voivodeship, county, district
    return "N/A", "N/A", "N/A"

def extract_offer_data(offer_url, headers):
    response = requests.get(offer_url, headers=headers)
    if response.status_code == 200:
        offer_soup = BeautifulSoup(response.content, "html.parser")
        title_element = offer_soup.find("h1", class_="css-1wnihf5 efcnut38")
        location_element = offer_soup.find("a", class_="e1w8sadu0 css-1helwne exgq9l20")
        price_element = offer_soup.find("strong", class_="css-1i5yyw0 e1l1avn10")
        area_element = offer_soup.find("div", class_="css-1wi2w6s enb64yk4")
        
        voivodeship, county, district = extract_location_data(location_element)

        title = title_element.get_text(strip=True) if title_element else "N/A"
        price = price_element.get_text(strip=True) if price_element else "N/A"
        area = area_element.get_text(strip=True) if area_element else "N/A"

        return {
            'Title': title,
            'Price': price,
            'Area': area,
            'Voivodeship': voivodeship,
            'County': county,
            'District': district
        }
    else:
        print(f"Failed to retrieve offer page: {offer_url}")
        return None

base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/dzialka/cala-polska?ownerTypeSingleSelect=ALL&viewType=listing&page="
offers_per_page = 36  # Liczba ofert do pobrania z jednej strony
start_page = 1
end_page = 100
all_data = []

for page in range(start_page, end_page + 1):
    print(f"Processing page {page}")

    url = f"{base_url}{page}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        offer_elements = soup.find_all("a", class_="css-1up0y1q e1dfeild2")

        if not offer_elements:
            break
        
        print(f"Found {len(offer_elements)} offer elements on page {page}")
        num_offers_to_process = min(offers_per_page, len(offer_elements))
        for i in range(num_offers_to_process):
            offer = offer_elements[i]
            offer_url = "https://www.otodom.pl" + offer['href']
            offer_data = extract_offer_data(offer_url, headers)
            if offer_data:
                all_data.append(offer_data)
        
        time.sleep(3)  # Dodaj opóźnienie między stronami, aby uniknąć blokady

    else:
        print("Failed to retrieve the main page.")
        break

df = pd.DataFrame(all_data, columns=['Title', 'Price', 'Area', 'Voivodeship', 'County', 'District'])
df.to_excel('offers1.xlsx', index=False)
print("Data saved to 'offers2.xlsx'")

