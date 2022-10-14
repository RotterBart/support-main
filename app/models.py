# -*- coding: utf-8 -*-
from app import db, login, app, search

from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt

from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy.orm.mapper import configure_mappers
from flask_login import current_user

class InstructionQuery(BaseQuery, SearchQueryMixin):
    pass


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


followers = db.Table(
    'followers', db.Column('follower_id', db.Integer,
                           db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Task', backref='executor', lazy='dynamic')
    posts = db.relationship('Post', backref="author", lazy="dynamic")
    dnstrings = db.relationship('DnString', backref='executor', lazy='dynamic')
    histories = db.relationship('ContactHistory', backref="chauthor", lazy="dynamic")
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(1024))
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')
    region = db.Column(db.String(100), default='all')
    reports = db.relationship('Report', backref='reporter', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {
                'reset_password': self.id,
                'exp': time() + expires_in
            },
            app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token,
                            app.config['SECRET_KEY'],
                            algorithm=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #def avatar(self, size):
    #    digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    #    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
    #        digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)

        return followed.union(own).order_by(Post.timestamp.desc())


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


"""
class AdPost(db.Model):

    __tablename__ = 'AdPost'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.String(512))
    price = db.Column(db.Integer)
    image = db.Column(db.String(1024))
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'))
    # category = db.relationship(
    #     'Category', backref=db.backref('AdPost', lazy=True))

    def __repr__(self):
        return '<AdPost {0}>'.format(self.title)
"""


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    instructions = db.relationship('Instruction',
                                   backref="category",
                                   lazy="dynamic")

    def __repr__(self):
        return 'Категория: {} {}'.format(self.id, self.name)


class Contact(db.Model):
    c_enterprise_id = db.Column(db.String(140), primary_key=True)
    c_string = db.Column(db.String(1024))
    c_description = db.Column(db.String(1024))
    workplacecount = db.Column(db.Integer)
    password = db.Column(db.String(1024))
    recdate = db.Column(db.DateTime, default=datetime.now)
    history = db.relationship('ContactHistory', backref="contact", order_by="ContactHistory.rec_date.desc()", lazy="dynamic")

class ContactHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enterprise_id = db.Column(db.String(140), db.ForeignKey('contact.c_enterprise_id'))
    event = db.Column(db.String(2048))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rec_date = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '{0}: {0}'.format(self.rec_date, self.event)

class CompendiumItem(db.Model):
    ci_id = db.Column(db.Integer, primary_key=True)
    dep_id = db.Column(db.Integer,
                       db.ForeignKey('department.dep_id'),
                       nullable=False)
    name = db.Column(db.String(140))
    phone = db.Column(db.String(140))
    desc = db.Column(db.String(140))

    def __repr__(self):
        return '<CompendiumItem {0} {0} {0}>'.format(self.ci_id, self.name,
                                                     self.dep_id)


class Department(db.Model):
    dep_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)

    contacts = db.relationship('CompendiumItem',
                               backref="department",
                               lazy="dynamic")

    def __repr__(self):
        return '<Department {0} {0}>'.format(self.dep_id, self.name)


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(1024))
    task_description = db.Column(db.Text())
    task_executor = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_executed = db.Column(db.Boolean, default=False)
    task_executed_timestamp = db.Column(db.DateTime, index=True)
    task_execution_description = db.Column(db.Text(), index=True)
    task_timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    task_limitdate = db.Column(db.DateTime, index=True)
    task_deleted = db.Column(db.Boolean, default=False)


class DnString(db.Model):
    dn_id = db.Column(db.Integer, primary_key=True)
    dnstring = db.Column(db.String(2048))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rec_date = db.Column(db.DateTime, index=True, default=datetime.now)


class Instruction(db.Model, SearchQueryMixin):
    query_class = InstructionQuery
    __tablename__ = 'instruction'

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(2048))
    trouble = db.Column(db.String())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    search_vector = db.Column(TSVectorType('trouble', 'theme'))
    deleted = db.Column(db.Boolean, default=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    report_body = db.Column(db.String())
    
        