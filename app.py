from datetime import datetime
from urllib import request
from flask import Flask, render_template,session, abort, redirect, request, url_for, send_from_directory,g,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.event import listens_for
from flask_admin import Admin,form, BaseView,expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink
import os.path as op 
from flask_migrate import Migrate
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
import os
from flask_mail import Mail, Message
import psycopg2

migrate = Migrate()
basedir = os.path.abspath(os.path.dirname(__file__))
file_path = op.join(op.dirname(__file__), 'static/files')
cert_path = op.join(op.dirname(__file__), 'static/cert')


app = Flask(__name__)

app.config['FLASK_APP'] = 'app.py'
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = 'anykey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'



   
# configuration of mail
app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = '1155121354@link.cuhk.edu.hk'
app.config['MAIL_PASSWORD'] = 'Nfp%^hc5pjpm3d$'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'   #lumen cyborg flatly
mail = Mail(app) # instantiate the mail class

ckeditor = CKEditor(app)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:ALDANM@localhost:5432/corp"
db = SQLAlchemy(app)
migrate.init_app(app, db)
admin = Admin(app, template_mode='bootstrap4')



@app.route("/forward/<string:user>/<string:phone>", methods=['GET','POST'])
def move_forward(user,phone):
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="corp",
        user='postgres',
        password='ALDANM')

    cursor = conn.cursor()
    sql = '''SELECT email from username'''
    # sql = '''DELETE FROM post1'''
    cursor.execute(sql)
    rows = cursor.fetchall()
    emails = []
    for row in rows:
        emails.append("{0}".format(row[0]))
    print(emails)
    msg = Message(
                    'Заказ Звонка',
                    sender ='1155121354@link.cuhk.edu.hk',
                    recipients = emails
                )
    msg.body = 'Поступил заказ от:\nКлиент:' +user +'\nНомер Телефона:' +phone +'\n'

    mail.send(msg)

    return redirect('/')

@app.route('/')
def index():
    session['logged_in'] = False
    session.clear()
    return render_template('index1.html')

# @babel.localeselector
# def get_locale():
#     return g.lang


# @app.before_request
# def before_request():
#     if request.view_args and 'lang' in request.view_args:
#         g.lang = request.view_args['lang']
#         request.view_args.pop('lang')
#     elif request.args.get('lang'):
#         g.lang = request.args.get('lang')
#     else:
#         g.lang = request.accept_languages.best_match({'en':'en', 'kz':'kz', 'ru':'ru'}.keys()) or 'en'
#     if g.lang not in {'en':'en', 'kz':'kz', 'ru':'ru'}:
#         abort(404)


# @app.route('/')
# def lang():
#     return render_template('index1.html', lang = g.lang)
    
class ImageView(ModelView):
    def is_accessible(self):
        if "logged_in" in session:  
            return True
        else:
            abort(403)
    form_overrides = dict(content=CKEditorField)
    create_template = 'edit.html'
    edit_template = 'edit.html'
    form_extra_fields = {
        'path': form.ImageUploadField('Image',
                                      base_path=file_path)
    }


class CertView(ModelView):
    def is_accessible(self):
        if "logged_in" in session:  
            return True
        else:
            abort(403)
    form_overrides = dict(content=CKEditorField)
    create_template = 'cert.html'
    edit_template = 'cert.html'
    form_extra_fields = {
        'path': form.ImageUploadField('Image',
                                      base_path=cert_path)
    }

class UserView(ModelView):
    def is_accessible(self):
        if "logged_in" in session:  
            return True
        else:
            abort(403)
    create_template = 'user_view.html'
    edit_template = 'user_view.html'


class User(db.Model):
    __tablename__ = 'username'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String)
    email = db.Column(db.String)
    login = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(64))


class Post(db.Model):
    __tablename__ = "post1"
    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.String(), unique=False, nullable=False)
    title_ru = db.Column(db.String(), unique=False, nullable=False)
    title_kz = db.Column(db.String(), unique=False, nullable=False)
    en = db.Column(db.Text(), nullable=False)
    ru = db.Column(db.Text(), nullable=False)
    kz = db.Column(db.Text(), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    path = db.Column(db.Unicode(128), nullable=False)


class Certificates(db.Model):
    __tablename__ = "cert"
    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.String(), unique=False, nullable=False)
    title_ru = db.Column(db.String(), unique=False, nullable=False)
    title_kz = db.Column(db.String(), unique=False, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    path = db.Column(db.Unicode(128), nullable=False)

# @app.route('/<lang>/login', methods = ["GET", "POST"])
# def login():
#     if request.method == "POST":
#         if request.form.get("username") == "admin" and  request.form.get("password") == "123456":
#             session['logged_in'] = True
#             return redirect("/admin")
#         else:
#             return render_template("login.html",login_1=_("Admin IMEC Login"),login_2=_("Sign in"), failed = True)

#     return render_template('login.html',login_1=_("Admin IMEC Login"),login_2=_("Sign in"))

@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and  request.form.get("password") == "123456":
            session['logged_in'] = True
            return redirect("/admin")
        else:
            return render_template("login.html", failed = True)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.clear()
    return redirect('/login')


@app.route('/news/<string:lol>')
def newsstr():
    return redirect('/news/1')
    

@app.route('/news')
def news():
    return redirect('/news/1')


@app.route('/news/<int:page_num>')
def news_articles(page_num):
   
    news_articles = Post.query.order_by(Post.id.desc()).paginate(page=page_num, per_page=4, error_out = True)
    return render_template("news.html", news_articles=news_articles)

@app.route('/cert')
def cert():
    cert = Certificates.query.order_by(Certificates.id.desc())
    return render_template("cert_page.html", cert=cert)

@app.route('/news_page/<int:num>')
def news_page(num):
    if num:
        news_articles = Post.query.filter_by(id= num)
        return render_template('news_page.html',news_articles=news_articles)
    else:
        return abort(403)


@app.route('/files/<filename>')
def uploaded_files(filename,target):
    path = app.config['UPLOADED_PATH']  
    print(app.config['UPLOADED_PATH']+'/'+filename)  
    flash(f(app.config['UPLOADED_PATH']+'/'+filename), 'success')
    return send_from_directory(path, target.id)


@app.route('/upload', methods=['POST'])
def upload(target):
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    flash(f(app.config['UPLOADED_PATH']+'/'+f.filename), 'success')
    f.save(os.path.join(app.config['UPLOADED_PATH'], target.id))
    url = url_for('uploaded_files', filename=target.id)
    return upload_success(url=url)


# @app.route('/admin/post/edit', methods=['POST'])
# def gettik(target):
#     f = request.files.get('upload')
#     extension = f.filename.split('.')[-1].lower()
#     if extension not in ['jpg', 'gif', 'png', 'jpeg']:
#         return upload_fail(message='Image only!')
#     print(app.config['UPLOADED_PATH']+'/'+f.filename)



@listens_for(Post, 'after_delete')
def del_image(target):
    if target.path:
        try:
            print(target.id)
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass

@listens_for(Certificates, 'after_delete')
def del_image(target):
    if target.path:
        try:
            print(target.id)
            os.remove(op.join(cert, target.path))
        except OSError:
            pass


admin.add_view(ImageView(Post, db.session, name='News'))
admin.add_view(CertView(Certificates, db.session, name='Certificates'))
admin.add_view(UserView(User, db.session, name='User'))
admin.add_link(MenuLink(name='Main page', endpoint='index'))
admin.add_link(MenuLink(name='Logout', endpoint='logout'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
