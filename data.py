import pandas as pd
import concurrent.futures
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

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
        offer_soup = BeautifulSoup(response.content, "html.parser")
        title_element = offer_soup.find("h1", class_="css-1wnihf5 efcnut38")
        location_element = offer_soup.find("a", class_="e1w8sadu0 css-1helwne exgq9l20")
        price_element = offer_soup.find("strong", class_="css-t3wmkv e1l1avn10")
        area_element = offer_soup.find("div", class_="css-1wi2w6s enb64yk4")
        
        if title_element is None or location_element is None or price_element is None or area_element is None:
            missing_elements = []
            if title_element is None:
                missing_elements.append("Title")
            if location_element is None:
                missing_elements.append("Location")
            if price_element is None:
                missing_elements.append("Price")
            if area_element is None:
                missing_elements.append("Area")
                
            print(f"Failed to retrieve offer page: {offer_url}, missing elements: {', '.join(missing_elements)}")
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

def process_package(chunk):
    package_data = []
    for link in chunk:
        offer_data = extract_offer_data(link)
        if offer_data:
            package_data.append(offer_data)
    return package_data

with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    all_data = []
    pbar = tqdm(total=num_threads, desc="Threads")
    futures = [executor.submit(process_package, chunk) for chunk in chunks]
    for future in concurrent.futures.as_completed(futures):
        package_data = future.result()
        all_data.extend(package_data)
        pbar.update(1)
    pbar.close()

df_result = pd.DataFrame(all_data, columns=['Title', 'Price', 'Area', 'Voivodeship', 'County', 'District'])
try:
    df_result.to_excel('results.xlsx', index=False)
    print("Combined data saved to 'results.xlsx'")
except Exception as e:
    print(f"Error saving data to Excel: {e}")
