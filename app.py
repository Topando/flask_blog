from datetime import datetime
from functools import wraps

import flask_login

from data.admins import Admin
from data.article import Article
from flask_login import current_user
from flask_login import LoginManager, UserMixin, login_required, logout_user, login_manager, login_user, current_user
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import Session, sessionmaker
from urllib3.packages.six import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from data.profile import Profile
from data.profile_update_form import ProfileForm
from data.get_admin_form import GetAdminForm

app = Flask(__name__, static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config['SECRET_KEY'] = 'a really really really really long secret key'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['TESTING'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)
from data import db_session
from data.users import User

db_session.global_init("db/blog.db")
db_sess = db_session.create_session()


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect('/login')

        else:
            return f(*args, **kwargs)

    return wrap


def check_admin():
    id = current_user.get_id()
    check = db_sess.query(Admin).filter(Admin.user_id == id).first()
    if check != None:
        return True
    else:
        return False



@manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(int(user_id))


@app.route('/login', methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated is False:
        login = request.form.get('login')
        password = request.form.get('password')
        if request.method == "POST":
            if login and password:
                user = db_sess.query(User).filter(User.login == login).first()
                if user and check_password_hash(user.password, password):
                    login_user(user)
                    return redirect(url_for("posts"))
                else:
                    return render_template("login.html", er="Логин или пароль введены неверно")
            else:
                return render_template("login.html", er="Ошибка авторизации")
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
    name = request.form.get("name")
    password = request.form.get('password')
    password2 = request.form.get('password2')
    if request.method == "POST":
        if not (login or password2 or password):
            return render_template("register.html", er="Введите данные")
        elif password != password2:
            return render_template("register.html", er="Пароли не совпадают")
        else:
            try:
                hash_pwd = generate_password_hash(password)
                new_user = User(login=login, name=name, password=hash_pwd)
                print(new_user.name)
                db_sess.add(new_user)
                db_sess.commit()
                return redirect('/login')
            except Exception:
                return render_template("register.html", er="Такой email уже существует")
        return render_template("register.html", er="Ошибка")

    else:
        return render_template('register.html')


@app.route('/')
@app.route('/home')
def index():
    return redirect('/posts')


@app.route('/posts')
def posts():
    article = Article()
    articles = db_sess.query(Article).all()
    print(articles)
    return render_template("posts.html", articles=articles, check_admin=check_admin())


@app.route('/posts/<int:id>')
@login_required
def post_detail(id):
    print(current_user.get_id())
    article = db_sess.query(Article).get(id)
    return render_template("post_detail.html", article=article, check_admin=check_admin())


@app.route('/posts/<int:id>/del')
def post_del(id):
    if check_admin():
        article = db_sess.query(Article).filter(Article.id == id).first()
        print(article)
        try:
            db_sess.delete(article)
            db_sess.commit()
            return redirect('/posts')
        except:
            return "При удалени статьи произошла ошибка"
    else:
        return redirect(f"/posts/{id}")


@app.route('/posts/<int:id>/update', methods=["POST", "GET"])
def post_update(id):
    if check_admin():
        article = db_sess.query(Article).get(id)
        if request.method == "POST":
            article.title = request.form["title"]
            article.intro = request.form["intro"]
            article.text = request.form["text"]
            try:
                db_sess.commit()
                return redirect('/posts')
            except:
                return "При добавлении стьатьи произошла ошибка"
        else:
            return render_template("post_update.html", article=article)
    else:
        return redirect(f"/posts/{id}")


@app.route('/profile')
def profile():
    profile_info = db_sess.query(Profile).filter(Profile.id == 1).first()
    return render_template("profile.html", profile=profile_info, check_admin=check_admin())


@app.route("/profile_update", methods=['GET', 'POST'])
def profile_update():
    if check_admin():
        profile_text = db_sess.query(Profile).filter(Profile.id == 1).first()
        form = ProfileForm(name=profile_text.name, about=profile_text.about, rewards=profile_text.rewards)
        if form.validate_on_submit():
            name = form.name.data
            about = form.about.data
            rewards = form.rewards.data
            try:
                db_sess.query(Profile).filter(Profile.id == 1).update({"name": name, "about": about, "rewards": rewards})
                db_sess.commit()
            except Exception:
                print("Бывает")
            return redirect(url_for("profile"))
        return render_template("profile_update.html", form=form)
    else:
        return redirect("/profile")


@app.route('/create-article', methods=["POST", "GET"])
def create_article():
    if check_admin():
        if request.method == "POST":
            title = request.form["title"]
            intro = request.form["intro"]
            text = request.form["text"]
            article = Article(title=title, intro=intro, text=text)
            try:
                print(article, text, intro, title)
                db_sess.add(article)
                db_sess.commit()

                return redirect('/posts')
            except:
                return "При добавлении стьатьи произошла ошибка"
        else:
            return render_template("create-article.html")
    else:
        return redirect("/posts")


@app.route("/get_admin", methods=["POST", "GET"])
def get_admin():
    form = GetAdminForm()
    print(current_user.get_id())
    if current_user.get_id() is not None:
        print(21312)
        if form.validate_on_submit():
            password = form.password.data
            print(password)
            if password == "1234":
                admin = Admin(user_id=current_user.get_id())
                db_sess.add(admin)
                db_sess.commit()
            return redirect("/posts")
        else:
            print(12312)
            return render_template("get_admin.html", form=form)
    return redirect("/posts")


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 404:
        return redirect(url_for('login_page') + "?next" + request.url)

    return response


@app.context_processor
def any_data_processor():
    if current_user.is_authenticated:
        id = current_user.get_id()
        user = db_sess.query(User).filter(User.id == id).first()
        name = user.name
        return dict(user_aunt=name, check_admin=True)
    else:
        return dict(user_aunt="None")
