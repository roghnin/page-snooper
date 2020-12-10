import my_web_driver
from bs4 import BeautifulSoup
import re
import json
import gmail
import os
from datetime import datetime
import pytz

base_urls = [{"name":"US", "url":"https://www.costco.com/CatalogSearch?dept=All&sortBy=item_added_date+desc&keyword="},
    {"name":"Canada", "url":"https://www.costco.ca/CatalogSearch?dept=All&sortBy=item_added_date+desc&keyword="}]
keywords = ["handbag"]

def get_name(dic):
    return dic['name']

def search_url_builder(base_url, keyword):
    # TODO: ugly.
    if (base_url["name"] == "Canada" and keyword == "handbag"):
        return "https://www.costco.ca/handbags.html?searchProvider=lucidworks&sortBy=item_added_date+desc"
    return base_url["url"]+keyword

def snoop():
    driver = my_web_driver.get_driver()
    for base_url in base_urls:
        for keyword in keywords:
            url = search_url_builder(base_url, keyword)
            driver.implicitly_wait(20) # seconds
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # costco-specific parsing:
            descs = soup.find_all("span", class_="description")
            curr_newest = []
            for desc in descs:
                item_raw = desc.find("a")
                curr_newest.append({'name':item_raw.get_text().strip('\t\n'), 'url':item_raw['href']})
            # curr_newest.sort(key = get_name)
            if (not curr_newest):
                print(driver.page_source)
            
            file_name = "costco_"+base_url["name"]+"_" +keyword+"_last_newest.json"
            if (not os.path.isfile(file_name)):
                json.dump([], open(file_name, "w"))
            dump_file = open(file_name, "r")
            last_newest = json.load(dump_file)
            if (last_newest and curr_newest[0] in last_newest):
                continue

            updates = []
            renewed = []
            for item in curr_newest:
                if item not in last_newest:
                    updates.append(item)
                else:
                    last_newest.remove(item)
                    renewed.append(item)
            
            # send messages
            if updates:
                message_text = "result page: "+url+"\n\n"
                for item in updates:
                    message_text += item["name"]+"\n"+item["url"]+"\n\n"
                gmail.send_messages("costco "+base_url["name"]+" "+keyword+" update @ "+datetime.now(pytz.timezone('US/Eastern')).strftime("%d/%m/%Y %H:%M:%S"), message_text)
            
            dump_file = open(file_name, "w")
            joined = updates + renewed + last_newest
            json.dump(joined[:100], dump_file, indent=4)

    dump_file.close()
    driver.close()
    driver.quit()

if __name__ == '__main__':
    snoop()