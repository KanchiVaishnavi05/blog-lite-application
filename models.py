from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from flask_login import UserMixin


class Accounts(db.Model,UserMixin):

    __tablename__="accounts"
    user_id=db.Column(db.String,primary_key=True)
    password=db.Column(db.String,nullable=False)
    name=db.Column(db.String,nullable=False)
    profile=db.Column(db.String)
    user_posts=db.relationship('Posts',foreign_keys='Posts.user_id',backref=db.backref('post_rel'),cascade='delete')
    user_followers=db.relationship('Follow',foreign_keys='Follow.user',backref=db.backref('user_rel'),cascade='delete')
    user_following=db.relationship('Follow',foreign_keys='Follow.following',backref=db.backref('following_rel'),cascade='delete')
    user_likes=db.relationship('Likes',foreign_keys='Likes.user_id',backref=db.backref('Likes_rel'),cascade='delete')
    def get_id(self):
            return (self.user_id)

class Posts(db.Model,UserMixin):
    __tablename__='posts'
    user_id=db.Column(db.String,db.ForeignKey("accounts.user_id"))
    post_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    post=db.Column(db.String,nullable=False)
    caption=db.Column(db.String)
    title=db.Column(db.String,nullable=False)
    timestamp=db.Column(db.String)
    # post_rel=db.relationship('Accounts',foreign_keys=[user_id])
    
    like=db.Column(db.Integer,db.ForeignKey("likes.post_id"))
    like_rel=db.relationship('Likes',uselist=True,foreign_keys=[like],cascade='delete')


class Likes(db.Model):
    __tablename__='likes'
    l_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    post_id=db.Column(db.Integer,db.ForeignKey("posts.post_id"))
    
    user_id=db.Column(db.String,db.ForeignKey('accounts.user_id'))
    

   
class Follow(db.Model):
    __tablename__="following"
    id=db.Column(db.Integer,autoincrement=True,primary_key=True)
    user=db.Column(db.String,db.ForeignKey("accounts.user_id"))
    # user_rel=db.relationship("Accounts",foreign_keys=[user])
    following=db.Column(db.String,db.ForeignKey("accounts.user_id"))
    # following_rel=db.relationship("Accounts",foreign_keys=[following])
