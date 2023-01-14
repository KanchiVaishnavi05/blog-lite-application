from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Accounts
from flask_restful import Api
from api import Accounts_api, Post_api, Follow_api, Like_api
import os
import requests
import datetime
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)

os.curdir
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + \
    os.path.join(basedir, "database.sqlite3")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db.init_app(app)
app.app_context().push()
db.create_all()
api = Api(app)
login_manager = LoginManager(app)
new_user = False


api.add_resource(Accounts_api, '/api/accounts',
                 '/api/accounts/<string:user_id>/<string:search>/<string:all>', '/api/accounts/<string:user_id>')
api.add_resource(Post_api, '/api/posts',
                 '/api/posts/<string:user_id>', '/api/posts/<string:p_id>')
api.add_resource(
    Follow_api, '/api/follow/<string:user_id>/<string:follower>', '/api/follow')
api.add_resource(Like_api, '/api/like', '/api/like/<string:post_id>')

api.init_app(app)
app.config['SECRET_KEY'] = "starting mission"


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    return Accounts.query.filter_by(user_id=user_id).first()


@app.route("/", methods=["GET", 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        data = Accounts.query.filter_by(user_id=user_id).first()
        if data:
            if str(data.password) == password:
                login_user(data, remember=True)
                user = current_user.user_id
                profile = user+'.jpg'
                name = current_user.name
                data = requests.get(request.root_url+'api/posts/'+'0').json()
                following = requests.get(
                    request.root_url+'api/follow/'+current_user.user_id+'/False')
        
                following = [x['following'] for x in following.json()]
                
                posts=[]
                
                for i in data:
                    
                    if i['user_id'] in following:
                        posts.append(i)
                return render_template('feed.html', icon=profile, name=name, posts=posts, following=following)
            else:
                return render_template('login.html', alert="wrong")
        else:
            return render_template('login.html', alert="create")
    else:
        if current_user.is_authenticated:
            data = requests.get(request.root_url+'api/posts/'+'0').json()
            profile = current_user.user_id+'.jpg'
            name = current_user.name
            following = requests.get(
                request.root_url+'api/follow/'+current_user.user_id+'/False')
            following = [x['following'] for x in following.json()]
            posts=[]
            
            for i in data:
                
                if i['user_id'] in following:
                    posts.append(i)
            return render_template('feed.html', icon=profile, name=name, posts=posts, following=following)
           
        return render_template('login.html', alert='False')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route("/templates/create.html", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        path = os.path.join('static//profiles//',
                            request.form['user_id']+'.jpg')
        img = request.files['profile']
        if img.filename != '':
            img.save(path)
        form = {"user_id": request.form['user_id'], 'fname': request.form['fname'],
                'lname': request.form['lname'], 'password': request.form['password'], 'profile': path}
        if requests.post(url=request.url_root+'api/accounts', json=form).status_code == 201:
            users = requests.get(url=request.root_url +
                                 'api/accounts/False/False/True').json()
            del users[-1]
            
            login_user(Accounts.query.filter_by(
                user_id=request.form['user_id']).first(), remember=True)
            following = requests.get(
            url=request.url_root+'api/follow/'+current_user.user_id+'/False')
            following = [x['following'] for x in following.json()]
            return render_template('users.html', users=users, current_user=current_user,following=following)
        else:
            return render_template('create.html', edit='False', error='already exist')
    else:
        if current_user.is_authenticated:
            users = requests.get(url=request.root_url +
                                 'api/accounts/False/False/True').json()
            following = requests.get(
            url=request.url_root+'api/follow/'+current_user.user_id+'/False')
            del users[-1]
            following = [x['following'] for x in following.json()]
            return render_template('users.html', users=users, current_user=current_user,following=following)

        return render_template('create.html', edit='False', error='')


@app.route('/templates/post.html', methods=['GET', 'POST'])
@login_required
def post():
    if request.method == 'POST':
        img = request.files['post']
        stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = stamp+current_user.user_id+img.filename
        path = os.path.join('static/posts/', filename)
        img.save(path)
        form = {'post': filename, 'title': request.form['title'],
                'caption': request.form['caption'], 'timestamp': stamp, 'user_id': current_user.user_id}
        if requests.post(url=request.url_root+'api/posts', json=form).status_code == 201:
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('profile'))
    else:
        return render_template('post.html', edit='False')


@app.route('/<string:following>/follow', defaults={'unfollow': None}, methods=["GET", "POST"])
@app.route('/<string:following>/<string:unfollow>/follow', methods=["GET", "POST"])
@login_required
def follow(following, unfollow):
    if unfollow == "True":
        entry = {'user': current_user.user_id, 'following': following}
        requests.delete(url=request.url_root+'api/follow', json=entry)
        return redirect(request.referrer)
    entry = {'user': current_user.user_id, 'following': following}
    requests.post(url=request.url_root+'api/follow', json=entry)
    return redirect(request.referrer)


@app.route('/profile', defaults={'var': 'post'}, methods=["GET", "POST"])
@app.route('/profile/<string:var>', methods=["GET", "POST"])
@login_required
def profile(var):
    posts = requests.get(url=request.url_root +
                         'api/posts/'+current_user.user_id)
    follower = requests.get(url=request.url_root +
                            'api/follow/'+current_user.user_id+'/True')
    following = requests.get(url=request.url_root +
                             'api/follow/'+current_user.user_id+'/False')
    followings = [x['following'] for x in following.json()]

    return render_template('profile.html', current_user=current_user, other_user=current_user, posts=posts.json(),
                           followers=follower.json(), following=following.json(), variable=var, followings=followings, other='False')

@app.route('/other_profile/<string:var>,<string:user_id>,<string:other>', methods=["GET", "POST"])
@login_required
def other_profile(var, user_id, other):
    other_user = requests.get(url=request.root_url +
                              'api/accounts/'+user_id+'/False/False').json()
    posts = requests.get(url=request.url_root +
                         'api/posts/'+user_id)
    follower = requests.get(url=request.url_root +
                            'api/follow/'+user_id+'/True')
    following = requests.get(url=request.url_root +
                             'api/follow/'+user_id+'/False')
    my_follower_list = [x['user'] for x in follower.json()]
    followings = [x['following'] for x in following.json()]
    return render_template('profile.html', current_user=current_user, other_user=other_user, posts=posts.json(),
                           followers=follower.json(), following=following.json(), variable=var, followings=followings, other=other, my_follower_list=my_follower_list)


@app.route('/search', methods=["GET", "POST"])
@login_required
def search():
    if request.method == "GET":
        username = request.args.get('uname', type=str)
        users = requests.get(url=request.url_root +
                             'api/accounts/'+username+'/True'+'/False')
        following = requests.get(
            url=request.url_root+'api/follow/'+current_user.user_id+'/False')
        following = [x['following'] for x in following.json()]
        return render_template('users.html', users=users.json(), current_user=current_user, following=following)


@app.route('/delete')
@login_required
def delete_user():
    if requests.delete(url=request.root_url+'api/accounts/'+current_user.user_id).status_code == 200:
        logout_user()
        return redirect('/')
    else:
        return redirect(url_for('profile'))


@app.route('/delete_post', methods=["GET", "POST"])
@login_required
def delete_post():
    if requests.delete(url=request.url_root+'api/posts/'+str(request.args.get('post_id'))).status_code == 200:
        return redirect(request.referrer)
    else:
        return redirect(url_for('profile'))


@app.route('/update_post', methods=["GET", 'POST', 'PUT'])
@login_required
def update_post():
    data = request.args.to_dict()
    if request.method == "GET":
        return render_template('post.html', data=data, edit='True')
    else:
        new_data = {'title': request.form.get(
            'title'), 'caption': request.form.get('caption')}
        if requests.put(url=request.root_url+'api/posts/'+request.args.get('post_id'), json=new_data).status_code == 200:
            return redirect(url_for('profile'))


@app.route('/update_profile', methods=["GET", "POST", "PUT"])
@login_required
def update_profile():
    if request.method == "GET":
        return render_template('create.html', edit='True', data=current_user)
    else:
        img = request.files.get('profile')
        if img.filename != "":
            path = os.path.join('static', 'profiles',
                                current_user.user_id+'.jpg')
            os.remove(path)
            img.save(path)
        form = {"user_id": current_user.user_id,
                'fname': request.form['fname'], 'lname': request.form['lname'], 'password': request.form['password']}
        if requests.put(url=request.root_url+'api/accounts', json=form).status_code == 200:
            return redirect(url_for("profile"))
        else:
            return redirect(url_for('profile'))


@app.route('/like/<string:post_id>/<string:profile>')
@login_required
def like(post_id,profile):
    data = {'id': post_id, 'user': current_user.user_id}
    requests.post(url=request.root_url+'api/like', json=data)
    if profile == "True":
        return redirect(request.referrer)
    return redirect(url_for('login',_anchor=post_id))


@app.route('/unlike/<string:post_id>/<string:profile>')
@login_required
def unlike(post_id,profile):
    data = {'id': int(post_id), 'user': current_user.user_id}
    requests.delete(url=request.root_url+'api/like', json=data)
    if profile == "True":
        return redirect(request.referrer)
    return redirect (url_for('login',_anchor=post_id))


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


if __name__ == "__main__":
    app.run(debug=True)
