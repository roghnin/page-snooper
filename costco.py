import requests
from bs4 import BeautifulSoup
from selenium import webdriver


base_url = "https://www.costco.com/CatalogSearch?dept=All&keyword="

def search_url_builder(keyword):
    return base_url+keyword

def snoop():
    url = search_url_builder("handbag")
    
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(executable_path=r"drivers/chromedriver", options=opts)
    driver.get("https://www.costco.com/")
    print(driver.page_source)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # costco-specific parsing:
    descs = soup.find_all("span", class_="description")
    # item_list = []
    for desc in descs:
        print (desc.contents[0])
    
    driver.close()
    driver.quit()

if __name__ == '__main__':
    snoop()