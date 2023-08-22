import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent

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
        price_element = offer_soup.find("strong", class_="css-t3wmkv e1l1avn10") #css-t3wmkv e1l1avn10 css-1i5yyw0 e1l1avn10
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
        print(f"Failed to retrieve offer page: {offer_url}, error {e}")
        return None

# chrome driver path
# DRIVER_PATH = r"/usr/lib/chromium-browser/chromedriver-linux64"
DRIVER_PATH = r"/usr/bin/chromedriver"

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1200")
options.add_argument(f"webdriver.chrome.driver=DRIVER_PATH")

ua = UserAgent()
user_agent = ua.random
options.add_argument(f'user-agent={user_agent}')

driver = webdriver.Chrome(options=options)
base_url = 'https://www.otodom.pl/pl/wyniki/sprzedaz/dzialka/cala-polska?limit=72'
# url = 'https://www.otodom.pl/pl/wyniki/sprzedaz/dzialka/cala-polska'


# ----- UR: -----
# https://www.otodom.pl/pl/wyniki/sprzedaz/dzialka/cala-polska?limit=72&page=2
# ---------------

# print(driver.page_source)
# all_links = driver.find_elements(By.CSS_SELECTOR, 'li.css-o9b79t.e1dfeild0 > a.css-1tiwk2i.e1dfeild2')
# all_links = driver.find_elements(By.CSS_SELECTOR, 'a.css-1tiwk2i.e1dfeild2')
# all_links = driver.find_elements(By.CLASS_NAME, 'css-1tiwk2i.e1dfeild2')


# print("OFERT Z OTODOM: ")
# print(len(all_links))
# for link in all_links:
    # print(link.get_attribute('href'))
    # print(link)

all_data = []
offer_count = 0
page_count = 1
page_limiter = 804 #804
offer_per_page = 75 #72
# df = pd.DataFrame(all_data, columns=['Link'])
start_time= time.time()
while True:

    if page_count == page_limiter+1:
        break
    url = base_url + "&page=" + str(page_count)
    driver.get(url)
    # print(url)
    print(page_count)
    for item in driver.find_elements(By.CLASS_NAME, 'css-1tiwk2i.e1dfeild2'):
        ActionChains(driver).move_to_element(item).perform()
        # time.sleep(0.1)
        # print(f"Nr: {offer_count}: {item.get_attribute('href')}")
        offer_url = item.get_attribute('href')
        # offer_data = extract_offer_data(offer_url)
        # if offer_data:
        all_data.append(offer_url)
        
        offer_count += 1
        if offer_count == offer_per_page:
            offer_count = 0
            page_count += 1
            # print(all_data)
            # df = df.append(all_data, ignore_index=True)
            # df.to_excel('all_links.xlsx', index=False)
            # all_data.clear()
            break

end_time = time.time()
print(end_time-start_time)               
driver.quit()

# base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/dzialka/cala-polska?ownerTypeSingleSelect=ALL&viewType=listing&page=1&limit=72"
# base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/dzialka/cala-polska"
# base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/dzialka/cala-polska?limit=72"
# page = 1
# max_pages = 1
# all_data = []



# while page <= max_pages:
#     print(f"Processing page {page}")

    # url = f"{base_url}&page={page}"
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    # response = requests.get(url, headers=headers)

    # if response.status_code == 200:
    #     soup = BeautifulSoup(response.content, "html.parser")
    #     # offer_elements = soup.find_all("a", href=True)
    #     offer_elements = soup.find_all("a", class_="css-1up0y1q e1dfeild2")
    #     # print(len(offer_elements))
        

    #     if not offer_elements:
    #         break

    #     for offer in offer_elements:
    #         # if offer["class"][1] == "e1dfeild2":
    #             # print(offer["class"][1])

    #         offer_url = "https://www.otodom.pl" + offer['href']
    #         offer_data = extract_offer_data(offer_url, headers)
    #         if offer_data:
    #             all_data.append(offer_data)

    #     page += 1
    # else:
    #     print("Failed to retrieve the main page.")
    #     print(f"fail on page:  {page}")

try:
    df = pd.DataFrame(all_data, columns=['Link'])
    df.to_excel('offers3.xlsx', index=False)
    print("Data saved to 'offers.xlsx'")
except Exception as e:
    print("cant save do xlsx file, error: ", e)
# t = time.localtime()
# current_time = time.strftime("%H:%M:%S", t)
# print(current_time)

# 170 sec dla 5 stron
# zrobić zapisywanie np co kilka stron
