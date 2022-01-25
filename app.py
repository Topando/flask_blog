from datetime import datetime
from functools import wraps

from flask_login import LoginManager, UserMixin, login_required, logout_user, login_manager, login_user, current_user
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import Session, sessionmaker
from urllib3.packages.six import wraps
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, static_folder="static")
app.secret_key = 'some secret salt'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['TESTING'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect('/login')

        else:
            return f(*args, **kwargs)

    return wrap


def check_admin():
    print(2143142)
    print(current_user.login == "f")
    if str(current_user.login) == 'sashae@gmail.com':
        return True
    return False

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return "<Admin %r" % self.id


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    intro = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Article %r" % self.id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def is_active(self):
        return True


@manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated is False:
        login = request.form.get('login')
        password = request.form.get('password')
        if request.method == "POST":
            if login and password:
                user = User.query.filter_by(login=login).first()
                if user and check_password_hash(user.password, password):
                    login_user(user)
                    return redirect(url_for("posts"))
                else:
                    flash("Логин или пароль введены неправильно")
            else:
                flash("Ошибка авторизации")
            return render_template('login.html')
        else:
            return render_template('login.html')
    else:
        return redirect(url_for('posts'))


@app.route('/logout', methods=["POST", "GET"])
def logout():
    logout_user()
    return redirect(url_for('posts'))


@app.route('/register', methods=["POST", "GET"])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == "POST":
        if not (login or password2 or password):
            flash("Введите данные")

        elif password != password2:
            flash("Пароли не совпадают")
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')
        return "ОШИБКА"

    else:
        return render_template('register.html')


@app.route('/')
@app.route('/home')
def index():
    return redirect("/posts")


@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()

    return render_template("posts.html", articles=articles)


@app.route('/posts/<int:id>')
@login_required
def post_detail(id):
    user = User.query.get(str(current_user).split(" ")[1][:-1])
    print(user)
    print(str(current_user).split(" ")[1][:-1])
    print(current_user.login)
    article = Article.query.get(id)
    return render_template("post_detail.html", article=article)


@app.route('/posts/<int:id>/del')
@login_required
def post_del(id):
    if check_admin() is True:
        article = Article.query.get_or_404(id)
        try:
            db.session.delete(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return "При удалени статьи произошла ошибка"
    else:
        return render_template("home_page.html")



@app.route('/posts/<int:id>/update', methods=["POST", "GET"])
@login_required
def post_update(id):
    if check_admin() is True:

        article = Article.query.get(id)
        if request.method == "POST":
            article.title = request.form["title"]
            article.intro = request.form["intro"]
            article.text = request.form["text"]
            try:
                db.session.commit()
                return redirect('/posts')
            except:
                return "При добавлении стьатьи произошла ошибка"
        else:
            return render_template("post_update.html", article=article)
    else:
        return render_template("home_page.html")


@app.route('/profile')
def profile():
    return render_template("profile.html")


@app.route('/create-article', methods=["POST", "GET"])
@login_required
def create_article():
    if check_admin() is True:
        if request.method == "POST":
            title = request.form["title"]
            intro = request.form["intro"]
            text = request.form["text"]
            article = Article(title=title, intro=intro, text=text)
            try:
                db.session.add(article)
                db.session.commit()
                return redirect('/posts')
            except:
                return "При добавлении стьатьи произошла ошибка"
        else:
            return render_template("create-article.html")
    else:
        return render_template("home_page.html")


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 404:
        return redirect(url_for('login_page') + "?next" + request.url)

    return response
