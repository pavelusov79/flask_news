import datetime

from sqlalchemy import DateTime, Table, String, Integer, Column, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_login import UserMixin
from slugify import slugify

from .database import Base


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    name = Column(String(50))
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    comments = relationship("Comments", back_populates="user", cascade="all, delete", passive_deletes=True)
    bookmarks = relationship("Bookmarks", back_populates="user", cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return f'User {self.username} {self.email}'


association_table = Table('association', Base.metadata, 
    Column('news_id', ForeignKey('news.id'), primary_key=True),
    Column('tags_id', ForeignKey('tags.id'), primary_key=True)
)


class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True) 
    tag_name = Column(String(128))
    slug = Column(String(128))
    news = relationship('News', secondary=association_table, back_populates='tags', lazy="dynamic")
    
    def save(self):
        self.slug = slugify(self.tag_name, ok='_', only_ascii=True)
        return self.slug

    def __repr__(self):
        return self.tag_name

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True) 
    title = Column(String(255))
    slug = Column(String(255))
    published = Column(Date)
    img = Column(String)
    news_text = Column(Text)
    news_url = Column(String)
    likes = Column(Integer, default=0)
    visits = Column(Integer, default=0)
    is_active = Column(Boolean)
    tags = relationship('Tags', secondary=association_table, back_populates='news', lazy="dynamic")
    comments = relationship("Comments", back_populates="news", cascade="all, delete", passive_deletes=True)
    bookmarks = relationship("Bookmarks", back_populates="news", cascade="all, delete", passive_deletes=True)

    def save(self):
        self.slug = slugify(self.title, ok='_', only_ascii=True)
        return self.slug
    
    def __repr__(self):
        return f'{self.published} {self.title}'


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    comment_text = Column(Text)
    comment_date = Column(DateTime(timezone=True), default=func.now())
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE")) 
    news_id = Column(Integer, ForeignKey('news.id', ondelete="CASCADE"))
    faild_moderation = Column(Text)
    is_active = Column(Boolean, default=False)
    user = relationship("User", back_populates="comments")
    news = relationship("News", back_populates="comments")

    def __repr__(self):
        return f'{self.comment_date} {self.user_id} {self.news_id}'


class Bookmarks(Base):
    __tablename__ = 'bookmarks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE")) 
    news_id = Column(Integer, ForeignKey('news.id', ondelete="CASCADE"))
    user = relationship("User", back_populates="bookmarks", passive_deletes=True)
    news = relationship("News", back_populates="bookmarks", passive_deletes=True)


class Statistics(Base):
    __tablename__ = 'statistics'
    id =  Column(Integer, primary_key=True)
    date = Column(Date, default=datetime.date.today())
    url = Column(String)
    

