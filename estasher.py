import os
import re
import requests
import shutil
import sys
from bs4 import BeautifulSoup
from slugify import slugify
from urllib.request import urlopen

save_location = '/tmp/ebay/'
item_id = sys.argv[1]
url = 'https://www.ebay.com/itm/'+item_id

if not os.path.exists(save_location):
    os.makedirs(save_location)

page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

ebay_title = soup.title.string.replace("  | eBay", '')

scripts = soup.findAll('script')

carousel = scripts[18].string

carousel_start = carousel.find('new enImgCarousel')
carousel_end = carousel.find('var pageLayer')
carousel_load = carousel[carousel_start:carousel_end]

images = re.findall(r"https:[a-zA-Z0-9\\\.\~\-]+-l1600\.jpg", carousel)

i = 0
max_images = len(images) / 3

for e in images:
    i += 1

    if i > max_images:
        continue

    thumb = e.encode().decode('unicode-escape')
    image_file = save_location+item_id+'-'+str(i).zfill(2)+'.jpg'

    r = requests.get(thumb, stream = True)
    r.raw.decode_content = True

    with open(image_file, 'wb') as f:
        shutil.copyfileobj(r.raw, f)


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
