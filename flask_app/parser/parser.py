import os
import datetime
import time
import requests

from pymongo import MongoClient
from lxml import html
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from PIL import Image


def parse_links():
    url_links = []
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
    url = 'https://anews.com/tag/novosti/'
    service = Service(os.path.dirname(__file__) + '/geckodriver')
    options = Options()
    options.add_argument('--window-size=1200, 800')
    options.headless = True
    driver = Firefox(options=options, service=service)
    driver.get(url)
    i = 0
    while i < 3:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(1)
        i += 1
    links = driver.find_elements(By.XPATH, '//a[@class="news-item__link"]')
    for link in links:
        url_links.append(link.get_attribute('href'))
    driver.close()
    return url_links


def get_news():
    client = MongoClient('127.0.0.1', 27017)
    db = client['flask_news']
    collection = db['main']
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'}
    urls = parse_links()
    for url in urls:
        db_item = {}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            db_item['url'] = url
            db_item['_id'] = int(url.split('/')[3].split('-')[0])
            if collection.count_documents({'_id': db_item['_id']}) == 0:
                dom = html.fromstring(res.text)
                db_item['title'] = dom.xpath('//h1/text()')[0]
                href = dom.xpath('//a[contains(@class, "post-info__time")]/@href')[0]
                db_item['published'] = datetime.datetime.strptime(href.split('/')[-2], "%Y-%m-%d")
                img = dom.xpath('//img[@class="img"]/@src')[0]
                path = os.path.dirname(__file__)
                dirpath = os.path.join(os.path.dirname(path), 'static/img/')
                os.makedirs(f'{dirpath}/{db_item["_id"]}', exist_ok=True)
                filename = os.path.join(f'{dirpath}{db_item["_id"]}/{img.split("/")[-1]}')
                if not os.path.exists(filename):
                    r = requests.get(img)
                    with open(filename, 'wb') as f:
                        f.write(r.content)
                org_img = Image.open(filename)
                width, height = org_img.size
                if width > 1200:
                    width_ratio = round(1200 / width * 100)
                    if org_img.mode == 'RGBA' or org_img.mode == 'P':
                        org_img = org_img.convert('RGB')
                    org_img.save(filename, quality=width_ratio)
                db_item['img'] = filename
                db_item['news_text'] = " ".join(dom.xpath('//p/text()'))
                tags = []
                news_tags = dom.xpath('//a[@class="post-bar__tag-link"]/text()')
                for i in news_tags:
                    tags.append(i.replace("#", ""))
                db_item['tags'] = tags
        collection.insert_one(db_item)
    return db


get_news()

