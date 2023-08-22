import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import threading
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.service import Service

def extract_location_data(location_element):
    location_parts = location_element.get_text(strip=True).split(',')
    if len(location_parts) >= 3:
        voivodeship = location_parts[-3].strip()
        county = location_parts[-2].strip()
        district = location_parts[-1].strip()
        return voivodeship, county, district
    else:
        return "N/A", "N/A", "N/A"

def extract_offer_data(offer_url, driver):
    try:
        driver.get(offer_url)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "css-1wnihf5")))
        offer_soup = BeautifulSoup(driver.page_source, "html.parser")
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
    except Exception as e:
        print(f"Failed to retrieve offer page: {offer_url}\nError: {e}")
        if driver.page_source:
            print("Page source:", driver.page_source)
        return None

def clean_duplicates(data):
    df = pd.DataFrame(data, columns=['Title', 'Price', 'Area', 'Voivodeship', 'County', 'District'])
    df.drop_duplicates(inplace=True)
    return df

chromedriver_executable = r'C:\\Program Files\\WebDriver\\chromedriver.exe'

# instancja  WebDriver
service = Service(executable_path=chromedriver_executable)

# opcja przeglądarki Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.binary_location = r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'

# instancja przeglądarki
driver = webdriver.Chrome(service=service, options=chrome_options)

input_file = 'offers3.xlsx'
df_links = pd.read_excel(input_file)
links = df_links['Link'].tolist()

num_threads = 8 
chunk_size = len(links) // num_threads
chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]

def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch data from {url}")
        return None

def process_package(links, start_idx, end_idx):
    package_data = []
    for i in range(start_idx, end_idx):
        offer_data = extract_offer_data(links[i], driver)
        if offer_data:
            package_data.append(offer_data)
    return package_data

driver = webdriver.Chrome(service=service)

# wątki i przetwarzanie paczek
all_data = []
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = []
    for i, chunk in enumerate(chunks):
        future = executor.submit(process_package, chunk, i * chunk_size, (i + 1) * chunk_size)
        futures.append(future)
    
    for future in futures:
        package_data = future.result()
        all_data.extend(package_data)


driver.quit()

# czyszczenie duplikatów i tworzenie DataFrame
df_result = clean_duplicates(all_data)

# zapis do pliku Excel
try:
    df_result.to_excel('results.xlsx', index=False)
    print("Combined data saved to 'results.xlsx'")
except Exception as e:
    print(f"Error saving data to Excel: {e}")
