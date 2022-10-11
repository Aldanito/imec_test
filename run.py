from ast import Mod
from contextlib import redirect_stderr
from datetime import datetime
from operator import truediv
from urllib import request

from flask import Flask, render_template,session, abort, redirect, request
from flask_sqlalchemy import SQLAlchemy

from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from mimesis import Person, Text

app = Flask(__name__)
app.config['FLASK_ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'anykey'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

person = Person('ru')
text = Text('ru')
class DashBoardView(AdminIndexView):
    @expose('/')
    def add_data_db(self):
        for i in range(10):
            if not len(User.query.all()) >= 10:
                user = User(username=person.full_name(), email=person.email(), password=person.password())
                db.session.add(user)
                db.session.commit()

                post = Post(title=text.title())
                db.session.add(post)

                comment = Comment(username=user.username, body='Клевая статья. Всем добра', post_id=post.id)
                db.session.add(comment)
            db.session.commit()
        all_posts = Post.query.all()
        all_comments = Comment.query.all()
        return self.render('admin/dashboard_index.html', all_posts=all_posts,
                           all_comments=all_comments)


admin = Admin(app, name='Admin', template_mode='bootstrap4', index_view=DashBoardView(), endpoint='admin')



@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and  request.form.get("password") == "123456":
            print(1)
            session['logged_in'] = True
            return redirect("/admin")
        else:
            return render_template("login.html", failed = True)

    return render_template('login.html')

@app.get('/')
def index():
    session['logged_in'] = False
    session.clear()
    return render_template('index1.html')
@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.clear()
    return redirect('/login')

    
@app.route('/admin')
def adminka():
    if session['logged_in'] == False:

        return redirect('/login')

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    last_seen = db.Column(db.DateTime)
    user_status = db.Column(db.String(40), nullable=True, default='Лучший пользователь проекта')
    tags = db.relationship('Tag', backref='user_tag', lazy=True, cascade="all, delete-orphan")
    posts = db.relationship('Post', backref='author', lazy=True)


class Post_ru(db.Model):
    __tablename__ = "posts_ru"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=False, nullable=False)
    content = db.Column(db.Text(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    comments = db.relationship('Comment', backref='article', lazy=True, cascade="all, delete-orphan")
    tags = db.relationship('Tag', backref='post_tag', lazy=True, cascade="all, delete-orphan")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)

class Post_eng(db.Model):
    __tablename__ = "posts_eng"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=False, nullable=False)
    content = db.Column(db.Text(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    comments = db.relationship('Comment', backref='article', lazy=True, cascade="all, delete-orphan")
    tags = db.relationship('Tag', backref='post_tag', lazy=True, cascade="all, delete-orphan")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)

class Post_kz(db.Model):
    __tablename__ = "posts_kz"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=False, nullable=False)
    content = db.Column(db.Text(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    comments = db.relationship('Comment', backref='article', lazy=True, cascade="all, delete-orphan")
    tags = db.relationship('Tag', backref='post_tag', lazy=True, cascade="all, delete-orphan")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    body = db.Column(db.Text(200), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    name = db.Column(db.Text(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)


class AnyPageView(BaseView):
    @expose('/')
    def any_page(self):
        return self.render('admin/any_page/index.html')



class SecureModuleView(ModelView):
    def is_accessible(self):
        if "logged_in" in session:  
            return True
        else:
            abort(403)
from flask_admin.base import MenuLink

admin.add_view(SecureModuleView(User, db.session))
admin.add_view(SecureModuleView(Post_ru, db.session))
admin.add_view(SecureModuleView(Post_kz, db.session))
admin.add_view(SecureModuleView(Post_eng, db.session))
admin.add_view(SecureModuleView(Comment, db.session))
admin.add_view(SecureModuleView(Tag, db.session))
admin.add_link(MenuLink(name='Main page', endpoint='index'))
admin.add_link(MenuLink(name='Logout', endpoint='logout'))

# admin.add_view(AnyPageView(name='Что-то еще'))



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
