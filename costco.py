import my_web_driver
from bs4 import BeautifulSoup
import re
import json
import gmail
import os
from datetime import datetime

base_url = "https://www.costco.com/CatalogSearch?dept=All&sortBy=item_added_date+desc&keyword="
keywords = ["handbag"]

def get_name(dic):
    return dic['name']

def search_url_builder(keyword):
    return base_url+keyword

def snoop():
    for keyword in keywords:
        url = search_url_builder(keyword)
        driver = my_web_driver.get_driver()
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # costco-specific parsing:
        descs = soup.find_all("span", class_="description")
        curr_newest = []
        for desc in descs:
            item_raw = desc.find("a")
            curr_newest.append({'name':item_raw.get_text().strip('\t\n'), 'url':item_raw['href']})
        # curr_newest.sort(key = get_name)
        
        file_name = keyword+"_last_newest.json"
        if (not os.path.isfile(file_name)):
            json.dump([], open(file_name, "w"))
        dump_file = open(file_name, "r")
        last_newest = json.load(dump_file)
        if (last_newest and last_newest[0] == curr_newest[0]):
            return

        dump_file = open(file_name, "w")
        json.dump(curr_newest, dump_file, indent=4)

        updates = []
        for item in curr_newest:
            if item not in last_newest:
                updates.append(item)

        # send messages
        if updates:
            message_text = ""
            for item in updates:
                message_text += item["name"]+"\n"+item["url"]+"\n\n"
            gmail.send_messages("costco "+keyword+" update @ "+datetime.now().strftime("%d/%m/%Y %H:%M:%S"), message_text)

        dump_file.close()
        driver.close()
        driver.quit()

if __name__ == '__main__':
    snoop()