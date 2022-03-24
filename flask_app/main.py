from flask import Blueprint, redirect, render_template, abort, request, jsonify, url_for, session
from flask_login import current_user, login_required
from sqlalchemy import or_
from sqlalchemy_paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Tags, News, Comments, Bookmarks, User, Statistics
from .database import db_session
from .forms import CommentForm


main = Blueprint('main', __name__)


def get_paginate(query, q_ty):
    page = request.args.get('page', default=1)
    paginator = Paginator(query, q_ty)
    try:
        p = paginator.page(page)
    except PageNotAnInteger:
        p = paginator.page(1)
    except EmptyPage:
        p = paginator.page(paginator.total_pages)
    return p


@main.route('/')
def index():
    news_last = News.query.order_by(News.id.desc()).first()
    news = News.query.filter(News.id!=news_last.id).order_by(News.id.desc())
    p = get_paginate(news, 18)
    session['page'] = request.full_path
    if 'search' in session:
        session.pop('search', '')
    if not 'host user' in session:
        session['host user'] = request.host_url
        st = Statistics(url=session['host user'])
        db_session.add(st)
        db_session.commit()
    return render_template('main/main.html', news_last=news_last, results=p)


@main.route('/news/<int:id>/<string:slug>/', methods=['GET', 'POST'])
def news_detail(id, slug):
    form = CommentForm()
    news_detail = News.query.get(id)
    comments = Comments.query.filter_by(news_id=news_detail.id, is_active=True).all()
    news_detail.visits += 1
    db_session.commit()
    if not news_detail:
        abort(404)
    bookmark = None
    if not current_user.is_anonymous:
        bookmark = Bookmarks.query.filter_by(user_id=current_user.id, news_id=news_detail.id).first()
    if form.validate_on_submit():
        comment = Comments(user_id=current_user.id, news_id=news_detail.id, comment_text=form.text.data)
        db_session.add(comment)
        db_session.commit()
        return redirect(url_for('main.news_detail', id=news_detail.id, slug=news_detail.slug))
    like = request.args.get('likes')
    bmark = request.args.get('bookmark')
    if like:
        total_likes = int(like) + 1
        news_detail.likes = total_likes
        db_session.commit()
        return jsonify({'data': news_detail.likes})
    if current_user and bmark:
        if bookmark:
            db_session.delete(bookmark)
        else:
            add_bookmark = Bookmarks(user_id=current_user.id, news_id=news_detail.id)
            db_session.add(add_bookmark)
        db_session.commit()
    return render_template('main/news_detail.html', news_detail=news_detail, form=form, bookmark=bookmark, comments=comments)


@main.route('/news/tag/<string:slug>/')
def news_slug(slug):
    tag = Tags.query.filter_by(slug=slug).first()
    if not tag:
        abort(404)
    p = get_paginate(tag.news.order_by(News.published.desc()), 12)
    return render_template('main/news_slug.html', tag=tag, results=p)


@main.route('/<int:id>/bookmarks/')
@login_required
def bookmarks(id):
    user = User.query.get(id)
    news_id = request.args.get('news_id')
    if news_id:
        bookmark = Bookmarks.query.filter_by(user_id=user.id, news_id=int(news_id)).first()
        db_session.delete(bookmark)
        db_session.commit()
        return redirect(url_for('main.bookmarks', id=user.id))
    return render_template('main/bookmarks.html', user=user)


@main.route('/search/')
def search():
    query = request.args.get('q')
    results = News.query.filter(or_(News.title.contains(i) for i in query.replace(',', '').split()) | News.tags.any(Tags.tag_name.in_(query.replace(',', '').split()))).order_by(News.published.desc())
    session['search'] = request.full_path
    p = get_paginate(results, 20)
    return render_template('main/search.html', results=p, query=query)

