import os
from flask import Flask, flash, render_template, request, redirect, url_for, \
    session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from excel_data.data_analysis import create_dirs, get_all_plots, \
    get_images_for_html, get_table_for_markets

UPLOAD_FOLDER = './excel_data/files'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres'
app.config['SECRET_KEY'] = 'SuPeR-puper-duper-secret-Key-value-+_)(*&^%$#@!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
migrate = Migrate(app, db)
create_dirs()
get_all_plots()


class User(db.Model):
    __tablename__ = 'users_for_test'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@app.route('/index.html')
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html',
                                   error='Invalid username or password')
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            if password != confirm_password:
                return render_template('register.html',
                                       error='Passwords do not match')
            username_check = User.query.filter_by(username=username).first()
            if username_check:
                return render_template('register.html',
                                       error='Username already taken!')
            email_check = User.query.filter_by(email=email).first()
            if email_check:
                return render_template('register.html',
                                       error='E-mail already taken!')
            new_user = User(username, email, password)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template('dashboard.html', user=user.username)
    else:
        return redirect(url_for('login'))


@app.route('/markets')
def markets():
    if 'user_id' in session:
        pics = get_images_for_html('markets')
        try:
            table = get_table_for_markets(file_name='P04_Stats.xlsx',
                                          sheet_name='Сети')
        except FileNotFoundError as error:
            table = '\nФайл c данными не найден! (%s)' % error
        return render_template('plots.html', pics=pics, table=table)
    else:
        return redirect(url_for('login'))


@app.route('/cm')
def cm():
    if 'user_id' in session:
        pics = get_images_for_html('cm')
        return render_template('plots.html', pics=pics)
    else:
        return redirect(url_for('login'))


@app.route('/kas')
def kas():
    pass


@app.route('/mr')
def mr():
    pass


@app.route('/upload')
def upload():
    if 'user_id' in session:
        return render_template('upload.html')
    else:
        return redirect(url_for('login'))


@app.route('/uploader', methods=['POST', 'GET'])
def uploader():
    if 'user_id' in session:
        if request.method == 'POST':
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Файл успешно загружен!')
                return redirect(url_for('upload', name=filename))
            else:
                flash('Ошибка!')
                return redirect(url_for('upload'))

    else:
        return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if 'user_id' in session:
        pass
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
