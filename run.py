from calendar import c
from datetime import datetime
from urllib import request
from flask import Flask, render_template,session, abort, redirect, request, url_for, send_from_directory,g,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.event import listens_for
from flask_admin import Admin, expose, AdminIndexView,form
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink
from os.path import exists
import os.path as op 
from flask_migrate import Migrate
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
from markupsafe import Markup
from flask_babel import Babel, gettext as _  # $ pip install flask-babel
import os
import werkzeug
from flask_mail import Mail


migrate = Migrate()
basedir = os.path.abspath(os.path.dirname(__file__))
file_path = op.join(op.dirname(__file__), 'static/files')

# available languages
LANGUAGES = {
    'en': {'flag':'en', 'name':'English'},
    'ru': {'flag':'ru', 'name':'Русский'},
    'kk': {'flag':'kk', 'name':'Қазақша'},
}


d = {
    'Read More': 'Read More', 
    'Return': 'Return', 
    'Previous': 'Previous', 
    'Next':'Next'
    }


app = Flask(__name__)
babel = Babel(app)

app.config['FLASK_APP'] = 'app.py'
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = 'anykey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'




mail = Mail(app)

ckeditor = CKEditor(app)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:ALDANM@localhost:5432/corp"
db = SQLAlchemy(app)
migrate.init_app(app, db)
admin = Admin(app, template_mode='bootstrap4')




@app.route('/')
def index():
    session['logged_in'] = False
    session.clear()
    return redirect(url_for('lang', lang=g.lang))


@babel.localeselector
def get_locale():
    return g.lang


@app.before_request
def before_request():
    if request.view_args and 'lang' in request.view_args:
        g.lang = request.view_args['lang']
        request.view_args.pop('lang')
    elif request.args.get('lang'):
        g.lang = request.args.get('lang')
    else:
        g.lang = request.accept_languages.best_match(LANGUAGES.keys()) or 'en'
    if g.lang not in LANGUAGES:
        abort(404)


@app.route('/<lang>')
def lang():
    return render_template('index1.html', l=_('en'), who=_('MAIN PAGE'), header_1=_("NEWS"), header_2=_("ITEMS"), header_3=_("SERVICES"), header_4=_("PURCHASING"), header_5=_("ABOUT"), header_6=_("VACANCIES"), header_7=_("CONTACTS"))

count = 0
    
class ImageView(ModelView):
    count+=1
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


@app.route('/<lang>/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and  request.form.get("password") == "123456":
            session['logged_in'] = True
            return redirect("/admin")
        else:
            return render_template("login.html",login_1=_("Admin IMEC Login"),login_2=_("Sign in"), failed = True)

    return render_template('login.html',login_1=_("Admin IMEC Login"),login_2=_("Sign in"))



@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.clear()
    return redirect('/ru/login')


@app.route('/<lang>/news/<string:lol>')
def newsstr(lol, lang):
    g.lang = lang
    return redirect(lang+'/news/1')
    

@app.route('/<lang>/news')
def news(lang):
    g.lang = lang
    return redirect(lang+'/news/1')


@app.route('/<lang>/news/<int:page_num>')
def news_articles(page_num):
   
    news_articles = Post.query.order_by(Post.id.desc()).paginate(page=page_num, per_page=4, error_out = True)
    return render_template("news.html", news_articles=news_articles, next = _(d['Next']), previous = _(d['Previous']), read = _(d['Read More']), l=_('en'),lang = lang,  who=_('MAIN PAGE'), header_1=_("NEWS"), header_2=_("ITEMS"), header_3=_("SERVICES"), header_4=_("PURCHASING"), header_5=_("ABOUT"), header_6=_("VACANCIES"), header_7=_("CONTACTS"))


@app.route('/<lang>/news_page/<int:num>')
def news_page(num):
    if num:
        print(Post.id)
        news_articles = Post.query.filter_by(id= num)
        return render_template('news_page.html', back = _(d['Return']), news_articles=news_articles,  l=_('en'),lang = lang,  who=_('MAIN PAGE'), header_1=_("NEWS"), header_2=_("ITEMS"), header_3=_("SERVICES"), header_4=_("PURCHASING"), header_5=_("ABOUT"), header_6=_("VACANCIES"), header_7=_("CONTACTS"))
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
    # if exists(file_path+/)
    # print(app.config['UPLOADED_PATH']+'/'+f.filename)
    flash(f(app.config['UPLOADED_PATH']+'/'+f.filename), 'success')
    f.save(os.path.join(app.config['UPLOADED_PATH'], target.id))
    url = url_for('uploaded_files', filename=target.id)
    return upload_success(url=url)
@app.route('/admin/post/edit', methods=['POST'])
def gettik(target):
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    # if exists(file_path+/)
    print(app.config['UPLOADED_PATH']+'/'+f.filename)
    # flash(f(app.config['UPLOADED_PATH']+'/'+f.filename), 'success')
    # f.save(os.path.join(app.config['UPLOADED_PATH'], target.id))
    # url = url_for('uploaded_files', filename=target.id)
    # return upload_success(url=url)

@listens_for(Post, 'after_delete')
def del_image(mapper, connection, target):
    if target.path:
        try:
            print(target.id)
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass


def rename_img():
    for count, filename in enumerate(os.listdir(file_path)):
        dst = f"NEWS_IMG {str(count)}.jpg"
        src =f"{file_path}/{filename}"  # foldername/filename, if .py file is outside folder
        dst =f"{file_path}/{dst}"
        os.rename(src, dst)
    flash(f"Account Succesfully created", "success")
    print(file_path)    


admin.add_view(ImageView(Post, db.session, name='News'))
admin.add_link(MenuLink(name='Main page', endpoint='index'))
admin.add_link(MenuLink(name='Logout', endpoint='logout'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
