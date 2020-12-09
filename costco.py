import requests
from bs4 import BeautifulSoup
from selenium import webdriver


base_url = "https://www.costco.com/CatalogSearch?dept=All&keyword="

def search_url_builder(keyword):
    return base_url+keyword

def snoop():
    url = search_url_builder("handbag")
    
    capabilities = webdriver.DesiredCapabilities.FIREFOX
    capabilities["marionette"] = True
    firefox_bin = "/usr/bin/firefox"
    opts = webdriver.FirefoxOptions()
    opts.add_argument("--headless")
    browser = webdriver.Firefox(firefox_binary=firefox_bin, capabilities=capabilities, executable_path="drivers/geckodriver", firefox_options=opts)
    page = browser.get(url)
    soup = BeautifulSoup(page, 'html.parser')

    # costco-specific parsing:
    descs = soup.find_all("span", class_="description")
    # item_list = []
    for desc in descs:
        print (desc.contents[0])
    
    web_driver.close()
    web_driver.quit()

if __name__ == '__main__':
    snoop()

