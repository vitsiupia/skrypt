import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup


def extract_location_data(location_element):
    location_parts = location_element.get_text(strip=True).split(',')
    if len(location_parts) >= 3:
        voivodeship = location_parts[-3].strip()
        county = location_parts[-2].strip()
        district = location_parts[-1].strip()
        return voivodeship, county, district
    else:
        return "N/A", "N/A", "N/A"

def extract_offer_data(offer_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(offer_url, headers=headers)
    try:
        offer_soup = BeautifulSoup(response.text, "html.parser")
        title_element = offer_soup.find("h1", class_="css-1wnihf5 efcnut38")
        location_element = offer_soup.find("a", class_="e1w8sadu0 css-1helwne exgq9l20")
        price_element = offer_soup.find("strong", class_="css-1i5yyw0 e1l1avn10")
        area_element = offer_soup.find("div", class_="css-1wi2w6s enb64yk4")

        if title_element is None or location_element is None or price_element is None or area_element is None:
            print(f"Failed to retrieve offer page: {offer_url}, missing elements")
            return None

        voivodeship, county, district = extract_location_data(location_element)

        title = title_element.get_text(strip=True)
        price = price_element.get_text(strip=True)
        area = area_element.get_text(strip=True)

        return {
            'Title': title,
            'Price': price,
            'Area': area,
            'Voivodeship': voivodeship,
            'County': county,
            'District': district
        }
    except Exception as e:
        print(f"Failed to retrieve offer page: {offer_url}, error {e}")
        return None


input_file = 'offers.xlsx'  
df_links = pd.read_excel(input_file)
links = df_links['Link'].tolist()

num_threads = 8  
chunk_size = len(links) // num_threads
chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]

def process_package(links):
    package_data = []
    for link in links:
        offer_data = extract_offer_data(link)
        if offer_data:
            package_data.append(offer_data)
    return package_data

all_data = []


with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = []
    for chunk in chunks:
        future = executor.submit(process_package, chunk)
        futures.append(future)
    
    for future in futures:
        package_data = future.result()
        all_data.extend(package_data)


df_result = pd.DataFrame(all_data, columns=['Title', 'Price', 'Area', 'Voivodeship', 'County', 'District'])
try:
    df_result.to_excel('results.xlsx', index=False)
    print("Combined data saved to 'results.xlsx'")
except Exception as e:
    print(f"Error saving data to Excel: {e}")
