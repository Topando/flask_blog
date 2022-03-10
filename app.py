import os

from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, logout_user, login_user, current_user
from urllib3.packages.six import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import desc

from data import db_session
from data.admins import Admin
from data.article import Article
from data.profile import Profile
from data.type import Type
from data.users import User

from data.create_article_form import CreateArticleForm
from data.get_admin_form import GetAdminForm
from data.profile_update_form import ProfileForm
from data.posts_form import PostsForm

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, './db/blog.db')
db_session.global_init(my_file)
db_sess = db_session.create_session()

app = Flask(__name__, static_folder="static")
app.config['SECRET_KEY'] = 'a really really really really long secret key'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['TESTING'] = False

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
    id = current_user.get_id()
    check = db_sess.query(Admin).filter(Admin.user_id == id).first()
    if check is not None:
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
                    return redirect("/posts")
                else:
                    return render_template("login.html", er="Логин или пароль введены неверно")
            else:
                return render_template("login.html", er="Ошибка авторизации")
            return render_template('login.html')
        else:
            return render_template('login.html')
    else:
        return redirect('/posts')


@app.route('/logout', methods=["POST", "GET"])
def logout():
    logout_user()
    return redirect('/posts')


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
                db_sess.add(new_user)
                db_sess.commit()
                return redirect('/login')
            except Exception:
                return render_template("register.html", er="Такой email уже существует")
        return render_template("register.html", er="Ошибка")

    else:
        return render_template('register.html')


@app.route('/home')
def index():
    return redirect('/posts')


def get_full_types():
    names = []
    for type in db_sess.query(Type).all():
        names.append(type.name)
    return names


@app.route('/', methods=["POST", "GET"])
@app.route('/posts', methods=["POST", "GET"])
def posts():
    form = PostsForm()
    form.types.choices += get_full_types()
    if request.method == "POST":
        type = form.types.data
        filters = form.filters.data
        if type != "Все записи":
            form.types.data = type
            types = db_sess.query(Type).filter(Type.name == type).first()
            if filters == "По дате (убываение)":
                articles_type = db_sess.query(Article).order_by(desc(Article.date)).filter(
                    Article.type == types.id).all()
            else:
                articles_type = db_sess.query(Article).order_by(desc(Article.date)).filter(
                    Article.type == types.id).all()
                articles_type.reverse()
        else:
            if filters == "По дате (убываение)":
                articles_type = db_sess.query(Article).order_by(desc(Article.date)).all()
            else:
                articles_type = db_sess.query(Article).order_by(desc(Article.date)).all()
                articles_type.reverse()

        return render_template("posts.html", articles=articles_type, check_admin=check_admin(), form=form)
    else:
        articles_type = db_sess.query(Article).order_by(desc(Article.date)).all()
        return render_template("posts.html", articles=articles_type, check_admin=check_admin(), form=form)


@app.route('/posts/<int:id>')
@login_required
def post_detail(id):
    article = db_sess.query(Article).get(id)
    print(article.type)
    print(db_sess.query(Type).filter(Type.id == article.type).first().name)
    return render_template("post_detail.html", article=article, check_admin=check_admin(),
                           type=db_sess.query(Type).filter(Type.id == article.type).first().name)


@app.route('/posts/<int:id>/del')
def post_del(id):
    if check_admin():
        article = db_sess.query(Article).filter(Article.id == id).first()
        try:
            db_sess.delete(article)
            db_sess.commit()
            return redirect('/posts')
        except Exception:
            return "При удалени статьи произошла ошибка"
    else:
        return redirect(f"/posts/{id}")


@app.route('/posts/<int:id>/update', methods=["POST", "GET"])
def post_update(id):
    article = db_sess.query(Article).filter(Article.id == id).first()
    form = CreateArticleForm(name=article.title, intro=article.intro, text=article.text)
    name = db_sess.query(Type).all()
    names = []
    for i in name:
        names.append(i.name)
    form.types.choices = names
    if check_admin():
        article = db_sess.query(Article).get(id)
        if request.method == "POST":
            if form.validate_on_submit():
                article.title = form.name.data
                article.intro = form.intro.data
                article.text = form.text.data
                type = form.types.data
                new_type = form.new_type.data
                if len(new_type) == 0:
                    article.type = db_sess.query(Type).filter(Type.name == type).first().id
                else:
                    if len(db_sess.query(Type).filter(Type.name == new_type).all()) == 0:
                        type = Type(name=new_type)
                        try:
                            db_sess.add(type)
                            db_sess.commit()
                        except Exception:
                            print("sorry")
                        article.type = db_sess.query(Type).filter(Type.name == new_type).first().id

                    else:
                        article.type = db_sess.query(Type).filter(Type.name == type).first()

                try:
                    db_sess.commit()
                    return redirect('/posts')
                except:
                    return "При добавлении стьатьи произошла ошибка"
        else:
            return render_template("post_update.html", article=article, form=form)
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
                db_sess.query(Profile).filter(Profile.id == 1).update(
                    {"name": name, "about": about, "rewards": rewards})
                db_sess.commit()
            except Exception:
                print("Бывает")
            return redirect("/profile")
        return render_template("profile_update.html", form=form)
    else:
        return redirect("/profile")


@app.route('/create-article', methods=["POST", "GET"])
def create_article():
    if check_admin():
        form = CreateArticleForm()
        name = db_sess.query(Type).all()
        names = []
        for i in name:
            names.append(i.name)
        if len(names) == 0:
            types = Type(name="сочинение")
            db_sess.add(types)
            db_sess.commit()
            names.append("сочинение")
        form.types.choices = names
        if request.method == "POST":
            if form.validate_on_submit():
                title = form.name.data
                intro = form.intro.data
                text = form.text.data
                type = form.types.data
                new_type = form.new_type.data
                if len(new_type) == 0:
                    id_type = db_sess.query(Type).filter(Type.name == type).first()
                else:
                    if len(db_sess.query(Type).filter(Type.name == new_type).all()) == 0:
                        type = Type(name=new_type)
                        try:
                            db_sess.add(type)
                            db_sess.commit()
                        except Exception:
                            print("sorry")
                        id_type = db_sess.query(Type).filter(Type.name == new_type).first()

                    else:
                        id_type = db_sess.query(Type).filter(Type.name == type).first()
                        print(id_type)
                article = Article(title=title, intro=intro, text=text, type=id_type.id)
                try:
                    db_sess.add(article)
                    db_sess.commit()

                    return redirect('/posts')
                except:
                    return "При добавлении стьатьи произошла ошибка"
            else:
                return render_template("create-article.html", form=form)
        else:
            return render_template("create-article.html", form=form)
    else:
        return redirect("/posts")


@app.route("/get_admin", methods=["POST", "GET"])
def get_admin():
    form = GetAdminForm()
    if current_user.get_id() is not None:
        if form.validate_on_submit():
            password = form.password.data
            if password == "1234":
                admin = Admin(user_id=current_user.get_id())
                db_sess.add(admin)
                db_sess.commit()
            return redirect("/posts")
        else:
            return render_template("get_admin.html", form=form)
    return redirect("/posts")


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 404:
        return redirect(('/login_page') + "?next" + request.url)

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


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_sess.close()
