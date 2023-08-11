import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

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

# Ścieżka do chromedriver.exe
chromedriver_executable = r'C:\Program Files\WebDriver\chromedriver.exe'

# Opcje przeglądarki Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")  # Dodanie opcji wyłączającej GPU, aby uniknąć wykrycia botów
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
chrome_options.add_argument(f"webdriver.chrome.driver={chromedriver_executable}")

# Tworzenie instancji przeglądarki
driver = webdriver.Chrome(options=chrome_options)

base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/dzialka/cala-polska?ownerTypeSingleSelect=ALL&viewType=listing&page=1&limit=72"
page = 1
max_pages = 1  # Zmień na żądaną liczbę stron
all_data = []

while page <= max_pages:
    print(f"Processing page {page}")

    url = f"{base_url}&page={page}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        offer_elements = soup.find_all("a", class_="css-1up0y1q e1dfeild2")

        if not offer_elements:
            print(f"No offer elements found on page {page}")
            break

        for offer in offer_elements:
            offer_url = "https://www.otodom.pl" + offer['href']
            offer_data = extract_offer_data(offer_url, driver)
            if offer_data:
                all_data.append(offer_data)

        # Przewijanie strony do kolejnej strony z ofertami
        page += 1
        if page <= max_pages:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Opóźnienie przed przejściem do następnej strony

            # Dodaj dodatkowe opóźnienie przed następnym żądaniem, aby uniknąć ograniczeń szybkości
            time.sleep(10)

    else:
        print(f"Failed to retrieve the main page. Status code: {response.status_code}")
        break

# Zamknięcie przeglądarki po zakończeniu analizy
driver.quit()

# Tworzenie DataFrame i zapis do pliku Excel
try:
    df = pd.DataFrame(all_data, columns=['Title', 'Price', 'Area', 'Voivodeship', 'County', 'District'])
    df.to_excel('offers.xlsx', index=False)
    print("Data saved to 'offers.xlsx'")
except Exception as e:
    print(f"Error saving data to Excel: {e}")
