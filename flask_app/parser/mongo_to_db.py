from pymongo import MongoClient
import sys
import os

sys.path.append(os.getcwd())

from flask_app.database import db_session
from flask_app.models import Tags, News


def transfer():
    client = MongoClient('127.0.0.1', 27017)
    db = client['flask_news']
    collection = db['main']
    for item in collection.find({}):      
        news_postgres = News.query.filter_by(id=item['_id']).first()
        if not news_postgres:
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
    db_session.close()

    
transfer()
