import os
import logging
from flask import Flask, flash, render_template, request, redirect, url_for, \
    session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from excel_data.data_analysis import create_dirs, get_all_plots, \
    get_images_for_html, get_table_for_markets, get_mr_list, get_mr_plots, \
    get_files_list, get_current_file_name

# logger configuration
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://postgres:postgres@pgdb:5432/postgres'
app.config['SECRET_KEY'] = 'SuPeR-puper-duper-secret-Key-value-+_)(*&^%$#@!'
app.config['UPLOAD_FOLDER'] = './excel_data/files'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
create_dirs()


# class for users
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,
                   primary_key=True)
    username = db.Column(db.String(80),
                         unique=True,
                         nullable=False)
    email = db.Column(db.String(100),
                      unique=True,
                      nullable=False)
    password = db.Column(db.String(120),
                         nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# route for index page
@app.route('/index.html')
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


# route for login page
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
            session['username'] = user.username
            return redirect(url_for('dashboard'))

        return render_template('login.html',
                               error='Invalid username or password')
    return render_template('login.html')


# route for register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
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
    return render_template('register.html')


# route for dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        file_name = get_current_file_name()
        file_list = get_files_list()
        return render_template('dashboard.html',
                               file_list=file_list,
                               file_name=file_name)
    return redirect(url_for('login'))


# route for markets page
@app.route('/markets')
def markets():
    if 'user_id' in session:
        pics = get_images_for_html('markets')
        pics_group = get_images_for_html('markets_group')
        file_name = get_current_file_name()
        if file_name:
            table = get_table_for_markets(file_name=file_name,
                                          sheet_name='Сети')
        else:
            table = None

        return render_template('plots.html',
                               pics=pics,
                               pics_group=pics_group,
                               table=table)
    return redirect(url_for('login'))


# route for cm page
@app.route('/cm')
def cm():
    if 'user_id' in session:
        pics = get_images_for_html('cm')
        return render_template('plots.html',
                               pics=pics)
    return redirect(url_for('login'))


# route for kas page
@app.route('/kas')
def kas():
    if 'user_id' in session:
        pics = get_images_for_html('kas')
        return render_template('plots.html',
                               pics=pics)
    return redirect(url_for('login'))


# route for mr page
@app.route('/mr', methods=['GET', 'POST'])
def mr():
    if 'user_id' in session:
        file_name = get_current_file_name()
        if file_name:
            mr_list = get_mr_list(file_name=file_name,
                                  sheet_name='MR')
            if request.method == 'GET':
                pics = get_images_for_html('mr')
                return render_template('mr.html',
                                       mr_list=mr_list,
                                       pics=pics)
            elif request.method == 'POST':
                mr_value = request.form.get('mr_value')
                if mr_value:
                    get_mr_plots(file_name, mr_value)
                    pics = get_images_for_html('mr')
                    return render_template('mr.html',
                                           mr_list=mr_list,
                                           pics=pics,
                                           mr_value=mr_value)

                flash('Ошибка!')
                return redirect(url_for('mr'))
        return render_template('mr.html',
                                   pics=None)
    return redirect(url_for('login'))


# route for uploader
@app.route('/uploader', methods=['POST', 'GET'])
def uploader():
    if 'user_id' in session:
        if request.method == 'POST':
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Файл успешно загружен!')
                return redirect(url_for('dashboard',
                                        name=filename))
            flash('Ошибка!')
            return redirect(url_for('dashboard'))

    return redirect(url_for('login'))


@app.route('/get_counts', methods=['POST', 'GET'])
def get_counts():
    if 'user_id' in session:
        if request.method == 'POST':
            file_name = request.form.get('file_name')
            if file_name:
                get_all_plots(file_name)
                return redirect(url_for('dashboard'))
            flash('Ошибка!')
            return redirect(url_for('dashboard'))

    return redirect(url_for('login'))


# route for profile page
@app.route('/profile')
def profile():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template('profile.html',
                               user=user)
    return redirect(url_for('login'))


# route for logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


# route for 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# for https with ssl
context = (r"./certificate.pem", r"./key.pem")

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        #        ssl_context=context,
        debug=False
    )
