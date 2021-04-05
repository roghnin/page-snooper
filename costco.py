import my_web_driver
from bs4 import BeautifulSoup
import re
import json
import gmail
import os
from datetime import datetime
import pytz
import time

base_urls = [{"name":"US", "url":"https://www.costco.com/CatalogSearch?dept=All&searchProvider=lucidworks&sortBy=item_added_date&keyword="},
    {"name":"Canada", "url":"https://www.costco.ca/CatalogSearch?sortBy=item_added_date&dept=All&keyword="}]
keywords = ["handbag"]

def get_name(dic):
    return dic['name']

def search_url_builder(base_url, keyword):
    # TODO: ugly.
    if (base_url["name"] == "Canada" and keyword == "handbag"):
        return "https://www.costco.ca/handbags.html?searchProvider=lucidworks&sortBy=item_added_date+desc"
    return base_url["url"]+keyword

def get_soup(url):
    print("getting soup of: " + url)
    start = time.time()
    driver = my_web_driver.get_driver()
    driver.implicitly_wait(3) # seconds
    driver.get(url)
    print("time used to get page:" + str(time.time()-start))
    ret = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    driver.quit()
    print("time used in total:" + str(time.time()-start))
    return ret

def is_item_valid(item):
    return "Product Not Found" not in get_soup(item["url"]).find("title").get_text()

def write_to_file(items, file_name):
    dump_file = open(file_name, "w")
    json.dump(items, dump_file, indent=4)
    dump_file.close()

def snoop():
    
    
    for base_url in base_urls:
        for keyword in keywords:
            print("keyword: " + keyword)
            url = search_url_builder(base_url, keyword)
            soup = get_soup(url)

            # costco-specific parsing to get all valid items on the first page:
            descs = soup.find_all("span", class_="description")
            curr_newest = []
            for desc in descs:
                item_raw = desc.find("a")
                item = {'name':item_raw.get_text().strip('\t\n'), 'url':item_raw['href']}
                if is_item_valid(item):
                    curr_newest.append(item)
                else:
                    print("dropping: " + str(item))
            # if we found nothing, print the source to see what's going on.
            if (not curr_newest):
                print("curr_newest is empty")
            
            # read the last (<=60) newest items from file.
            file_name = "costco_"+base_url["name"]+"_" +keyword+"_last_newest.json"
            if (not os.path.isfile(file_name)):
                dump_file = open(file_name, "w")
                json.dump([], dump_file)
                dump_file.close()
            dump_file = open(file_name, "r")
            last_newest = json.load(dump_file)

            # remove invalid items in last_newest.
            # last_newest = [item for item in last_newest if is_item_valid(driver, item)]
            # for testing:
            last_newest_tmp = []
            print("going over last_newest_tmp")
            for item in last_newest:
                if is_item_valid(item):
                    last_newest_tmp.append(item)
                else:
                    print("dropping: " + str(item))
            last_newest = last_newest_tmp

            # if the current newest is in last_newest, nothing new is coming up. skip this iteration.
            # if (last_newest and curr_newest[0] in last_newest):
            #     write_to_file(last_newest, file_name)
            #     continue
            
            # find actual updates in curr_newest, and renew seen stuff.
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
            
            # write combined results to file:
            joined = updates + renewed + last_newest
            write_to_file(joined[:60], file_name)

if __name__ == '__main__':
    snoop()