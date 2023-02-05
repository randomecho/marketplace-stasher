import os
import re
import requests
import shutil
import sys
from bs4 import BeautifulSoup
from slugify import slugify
from urllib.request import urlopen

if len(sys.argv) != 2:
    print("Missing item number")
    exit()

save_location = '/tmp/ebay/'
item_id = sys.argv[1]
url = 'https://www.ebay.com/itm/'+item_id
images_found = 0

if not os.path.exists(save_location):
    os.makedirs(save_location)

def get_images(page_source):
    all_scripts = page_source.findAll('script')

    for script_block in all_scripts:
        if script_block.string is not None and script_block.string.find('ZOOM_GUID') != -1:
            carousel = script_block.string
            carousel_start = carousel.find('mediaList')
            carousel_end = carousel.find('imageContainerSize')
            carousel_load = carousel[carousel_start:carousel_end]
            images = re.findall(r"https:\/\/i.ebayimg.com\/images\/g\/[a-zA-Z0-9]+/s-l1600\.jpg", carousel_load)

            image_counter = 0

            for e in images:
                thumb = e.encode().decode('unicode-escape')
                image_file = save_location+item_id+'-'+str(image_counter).zfill(2)+'.jpg'

                r = requests.get(thumb, stream = True)
                r.raw.decode_content = True

                with open(image_file, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                    image_counter += 1

    return image_counter


page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

ebay_title = soup.title.string.replace("  | eBay", '')

images_found = get_images(soup)

url_desc = 'https://vi.vipr.ebaydesc.com/ws/eBayISAPI.dll?ViewItemDescV4&item='+item_id+'&t=0&excSoj=1&excTrk=1&lsite=0&ittenable=true&domain=ebay.com&descgauge=1&cspheader=1&oneClk=2&secureDesc=1'
page_desc = urlopen(url_desc)
html_desc = page_desc.read().decode("utf-8")
soup_desc = BeautifulSoup(html_desc, "html.parser")

ebay_desc = soup_desc.get_text(separator=u"\n\n").replace('eBay', '').strip()

info = ebay_title + "\n\n- - - - - -\n\n" + ebay_desc

desc_file = save_location+slugify(ebay_title).lower()+".txt"

with open(desc_file, 'w') as f:
    f.write(info)

f.close()

if len(ebay_desc.strip()) > 0:
    print("Saved description at {}".format(desc_file))

if images_found > 0:
    print("Saved {} images".format(images_found))
