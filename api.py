from flask import Flask,request
from flask_restful import Api,Resource,marshal_with,fields
from models import Accounts,Posts,Follow,Likes
from models import db
import os
from datetime import datetime as dt
app=Flask(__name__)
api=(Api(app))

# class Login_api(Resource):
#     output= {"user_id":fields.String,
#             "password":fields.String}
#     def post(self,uname,passweor)

class Accounts_api(Resource):
    output= {"user_id":fields.String,
            "password":fields.String,
            "name":fields.String,
            "profile":fields.String}
    @marshal_with(output)
    def get(self,user_id,search,all):
        if search == "False" and all == 'False':
            user=Accounts.query.filter_by(user_id=user_id).first()
            if user:
                return user,200
            return '',404
        elif all == 'True':
            return Accounts.query.all()
        else:
            user=Accounts.query.filter(Accounts.name.ilike('%'+user_id+'%')).all()
            # print(user_id)
            return user
    
    @marshal_with(output)
    def post(self):
        data=request.get_json()
        user=Accounts(user_id=data.get('user_id'),name=data.get('fname')+' '+data.get('lname'),password=data.get('password'),profile=data.get('profile'))
        if Accounts.query.filter_by(user_id=user.user_id).first():
            return "",404

        db.session.add(user)
        db.session.commit()
        return data,201
    def put(self):
        data=request.get_json()
        # print(data)
        user=Accounts.query.filter_by(user_id=data['user_id']).first()
        if data['password'] != "":
            user.name=data['fname']+' '+data['lname']
            user.password=data['password']
        else:
            user.name=data['fname']+' '+data['lname']
        db.session.commit()
        return 200
    def delete(self,user_id):
        Follow.query.filter_by(user=user_id).delete()
        Follow.query.filter_by(following=user_id).delete()
        posts=Posts.query.filter_by(user_id=user_id).all()
        # print(posts)
        for post in posts:
            path=os.path.join('static','posts',post.post)
            os.remove(path)
            db.session.delete(post)
        Accounts.query.filter_by(user_id=user_id).delete()
        path=os.path.join('static','profiles',user_id+'.jpg')
        os.remove(path)
        db.session.commit()
        return 200


class Post_api(Resource):
    output={'post_id':fields.String,
            'post':fields.String,
            'title':fields.String,
            'caption':fields.String,
            'timestamp':fields.String,
            'timestamp':fields.String(attribute=lambda x:dt.strptime(x.timestamp,"%Y_%m_%d_%H_%M_%S").strftime('%d-%m-%Y %I:%M %p')),
            'path':fields.String,
            'user_id':fields.String,
            'name':fields.String(attribute=lambda x:x.post_rel.name),
            'liked_by':fields.Raw(attribute=lambda x:[i.user_id for i in x.like_rel])
    }
    @marshal_with(output)
    def post(self):
        data=request.get_json()
        post=Posts(post=data.get('post'),title=data.get('title'),caption=data.get('caption'),timestamp=data.get('timestamp'),user_id=data.get('user_id'))
        db.session.add(post)
        db.session.commit()
        # print(data)
        return 201
    @marshal_with(output)
    def get(self,user_id):
        if user_id=='0':
            data=Posts.query.all()
        else:
            data=Posts.query.filter_by(user_id=user_id).all()
            
        data=sorted(data,key=lambda x: x.timestamp,reverse=True)
        return data,201

    def put(self,user_id):
        data=request.get_json()
        post=Posts.query.filter_by(post_id=user_id).first()
        post.title=data.get('title')
        post.caption=data.get('caption')
        db.session.commit()
        return data ,200
    def delete(self,user_id):
        post=Posts.query.filter_by(post_id=int(user_id)).first()
        # print(post)
        # print(post.json())
        path=os.path.join('static','posts',post.post)
        os.remove(path)
        db.session.delete(post)
        db.session.commit()
        return 200 
class Follow_api(Resource):
    output={
        'user':fields.String,
        'following':fields.String,
        'names':fields.String(attribute=lambda x:x.user_rel.name),
        'fnames':fields.String(attribute=lambda  x: x.following_rel.name)
    }

    def post(self):
        data=request.get_json()
        follow=Follow(user=data.get('user'),following=data.get('following'))
        db.session.add(follow)
        db.session.commit()
        return "",201
    @marshal_with(output)
    def get(self,user_id,follower):
        if follower == "True":
            data=Follow.query.filter_by(following=user_id).all()
            
        else:
            data=Follow.query.filter_by(user=user_id).all()
        return data,200
    def delete(self):
        data=request.get_json()
        Follow.query.filter_by(user=data.get('user'),following=data.get('following')).delete()
        
        db.session.commit()
        return 200


class Like_api(Resource):
    output={
        'post_id':fields.Integer,
        'user_id':fields.String
    }
    @marshal_with(output)
    def get(self):
        data=Likes.query.all()
        return data,200
    def post(self):
        data=request.get_json()
        like=Likes(post_id=data.get('id'),user_id=data.get('user'))
        print(like)
        db.session.add(like)
        db.session.commit()
        return 200
    def delete(self):
        data=request.get_json()
        Likes.query.filter_by(post_id=data.get('id'),user_id=data.get('user')).delete()
        db.session.commit()
        return 200