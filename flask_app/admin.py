import datetime

from flask import Blueprint, abort, request
from werkzeug.security import generate_password_hash
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_mail import Message
from flask_admin import expose

from . import mail, admin
from .database import db_session
from .models import User, Comments, Tags, News, Statistics


admin_app = Blueprint('admin_panel', __name__)


class FlaskAppModelView(ModelView):
        page_size = 20

        def is_accessible(self):
            if current_user.is_anonymous or not current_user.is_admin:
                abort(403)
            else:
                return current_user.is_admin

    
class UserView(FlaskAppModelView):
    column_exclude_list = ['password']
    column_searchable_list = ['username']
    form_excluded_columns = ['comments', 'bookmarks']
    column_filters = ['is_admin']

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = generate_password_hash(request.form.get('password'))
            return model.password


class NewsView(FlaskAppModelView):
    column_filters = ['published']
    column_exclude_list = ['slug', 'news_url', 'news_text', 'img']
    form_excluded_columns = ['comments', 'bookmarks']
    form_widget_args = {
        'news_text': {'rows': 8}
    }


class TagsView(FlaskAppModelView):
    column_searchable_list = ['tag_name']


class CommentsView(FlaskAppModelView):
    column_exclude_list = ['faild_moderation', 'comment_text']
    column_searchable_list = ['user.username']
    column_filters = ['is_active']
    
    def on_model_change(self, form, model, is_created=False):
        fail_moder = request.form.get('faild_moderation')
        user_email = model.user.email
        if fail_moder:
            msg = Message('сообщение с портала NewsBlog', recipients=[user_email])
            msg.body = fail_moder
            mail.send(msg)
        return fail_moder


class StatistcsView(FlaskAppModelView):
    @expose('/')
    def edit_view(self):
        data_1 = request.args.get('data_1')
        data_2 = request.args.get('data_2')
        st = 0
        if data_1 and data_2:
            data_1 = datetime.datetime.strptime(data_1, '%Y-%m-%d')
            data_2 = datetime.datetime.strptime(data_2, '%Y-%m-%d')
            st = Statistics.query.filter(Statistics.date >= data_1, Statistics.date <= data_2).all()
        return self.render('admin/statistics.html', data_1=data_1, data_2=data_2, st=st)


admin.add_view(UserView(User, db_session, category='Auth'))
admin.add_view(NewsView(News, db_session, category='Main'))
admin.add_view(TagsView(Tags, db_session, category='Main'))
admin.add_view(CommentsView(Comments, db_session, category='Main'))
admin.add_view(StatistcsView(Statistics, db_session, category='Main'))
        
