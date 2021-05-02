import requests
import json
import base64
import yadisk
import os
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.utils import redirect, secure_filename
from data import db_session
from data.loginform import LoginForm
from data.users import User
from data.books import Book
from data.uploadbookform import UploadBookForm
from forms.user import RegisterForm
from pathlib import Path
from data import __all_models


UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'data/files/')
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('main.html')


@app.route('/developers')
def developers():
    return render_template('developers.html')


@app.route('/catalog')
def catalog():
    db_sess = db_session.create_session()
    books = db_sess.query(Book).all()
    for i in books:
        i.cover_image = str(base64.b64encode(i.cover_image))[2:-1]
    return render_template('catalog.html', title='Каталог', books=books)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/reading_book/<id>', methods=['GET', 'POST'])
def reading_book(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id).first()
    name = book.name
    response = requests.get(f'https://cloud-api.yandex.net/v1/disk/resources/download/?path={name}.txt',
                       headers={'Authorization': 'OAuth AQAAAAAer1ioAAcUyU5d7ZA8dkJhpuOWMzdNQAc'})
    download_link = response.json()["href"]
    
    req = requests.get(download_link, allow_redirects=True)

    books_text = req.content.decode('windows-1251')

    return render_template('reading_book.html', title=name, books_text=books_text)


@app.route('/upload_book', methods=['GET', 'POST'])
def upload_book():
    y = yadisk.YaDisk(token='AQAAAAAer1ioAAcUyU5d7ZA8dkJhpuOWMzdNQAc')
    db_sess = db_session.create_session()
    form = UploadBookForm()
    if form.validate_on_submit():
        cover_image_file = request.files['cover_image']
        if cover_image_file and allowed_file(cover_image_file.filename):
            filename = secure_filename(cover_image_file.filename)
            cover_filename = f"cover.{filename.split('.')[-1]}"
            cover_image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cover_filename))

        book_file = request.files['book_file']
        if cover_image_file and allowed_file(book_file.filename):
            #filename = secure_filename(book_file.filename)
            book_filename = 'book.txt'
            book_file.save(os.path.join(app.config['UPLOAD_FOLDER'], book_filename))

        y.upload(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'data/files/{book_filename}'), f'{form.bookname.data}.txt')
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'data/files/{cover_filename}'), 'rb') as file:
            file = file.read()
        published = requests.put(f'https://cloud-api.yandex.net/v1/disk/resources/publish/?path={form.bookname.data}.txt',
                                 headers={'Authorization': 'OAuth AQAAAAAer1ioAAcUyU5d7ZA8dkJhpuOWMzdNQAc'})
        response = requests.get(f'https://cloud-api.yandex.net/v1/disk/resources/?path={form.bookname.data}.txt',
                                headers={'Authorization': 'OAuth AQAAAAAer1ioAAcUyU5d7ZA8dkJhpuOWMzdNQAc'})
        book = Book(name=form.bookname.data,
                    author=form.author.data,
                    download_link=response.json()['public_url'],
                    description=form.description.data,
                    reading_time=form.reading_time.data,
                    cover_image=file)
        db_sess.add(book)
        db_sess.commit()

        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'data/files/{book_filename}')
        img_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'data/files/{cover_filename}')
        os.remove(file_path)
        os.remove(img_path)

        return redirect('/catalog')
    return render_template('upload_book.html', title='Добавление книги', form=form)


@app.route('/delete_book/<book_name>', methods=['GET', 'POST'])
def delete_book(book_name):
    y = yadisk.YaDisk(token='AQAAAAAer1ioAAcUyU5d7ZA8dkJhpuOWMzdNQAc')
    y.remove(f"{book_name}.txt", permanently=True)
    db_sess = db_session.create_session()
    db_sess.query(Book).filter(Book.name == book_name).delete()
    db_sess.commit()
    return redirect('/catalog')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
