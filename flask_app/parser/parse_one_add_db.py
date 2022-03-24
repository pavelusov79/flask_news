import requests
import os
import datetime
import pytz
import sys

from pymongo import MongoClient
from lxml import html
from PIL import Image

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from flask_app.database import db_session
from flask_app.models import Tags, News


def get_one_news():
    client = MongoClient('127.0.0.1', 27017)
    db = client['flask_news']
    collection = db['main']
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'}
    url = 'https://anews.com/tag/novosti/'
    res = requests.get(url, headers=headers)
    dom = html.fromstring(res.text)
    link = dom.xpath('//a[@class="news-item__link"]/@href')[0]
    r = requests.get(link, headers=headers)
    if r.status_code == 200:
        item_id = int(link.split('/')[3].split('-')[0])
        dom = html.fromstring(r.text)
        if collection.count_documents({'_id': item_id}) == 0:
            db_item = {}
            db_item['url'] = link
            db_item['_id'] = item_id
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


def transfer():
    client = MongoClient('127.0.0.1', 27017)
    db = client['flask_news']
    collection = db['main']
    q = collection.find({}).sort('_id', -1).limit(1)
    for item in q:      
        news_postgres = News.query.filter_by(id=item['_id']).first()
        print('-------------------')
        if not news_postgres:
            print('ok')
            add_news = News(id=item['_id'],
                            title=item['title'],
                            published=item['published'],
                            news_text=item['news_text'],
                            img=item['img'],
                            news_url=item['url'],
                            is_active=True
                            )
            
            t = []
            tags = item['tags']
            for tag in tags:
                ts = Tags.query.filter_by(tag_name=tag).first()
                if not ts:
                    add_tag = Tags(tag_name=tag)
                    add_tag.save()
                    db_session.add(add_tag)
                    db_session.commit()
                    t.append(add_tag)
                else:
                    t.append(ts)
            add_news.tags = t
            add_news.save()
            db_session.add(add_news)
            db_session.commit()
            logger_path = os.path.join(os.path.dirname(__file__), 'logger.txt')
            print('****added successfully****')
            with open(logger_path, 'a') as f:
                f.write(f"OK *** last news was added ***{datetime.datetime.now(pytz.timezone('Asia/Vladivostok')).strftime('%d.%m.%y %H:%M')} ***\n")
    db_session.close()


get_one_news()

transfer()


