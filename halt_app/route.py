import flask_login
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from halt_app import app, db, message_manager
from users_db.user_model import User
from users_db.user_api import get_user_info_by_login
from firebase_db.message_api import MessageAPI
from firebase_db.image_api import ImageAPI


message_api = MessageAPI()
image_api = ImageAPI()


@app.route('/', defaults={'username': None}, methods=['GET', 'POST'])
@app.route('/<username>', methods=['GET', 'POST'])
def home(username=None):
    if request.method == 'POST':
        new_post = request.form.get('post')
        file = request.files['file']

        # TODO зробити перевірку на зображення

        if new_post or file:
            user_id = flask_login.current_user.get_id()
            try:
                image_name = image_api.upload_image(file)
            except Exception:
                flash('Image error') if file else None
                image_name = None
            message_api.create_message(user_id, message_text=new_post, image_hash_name=image_name)

            return redirect(url_for('home'))
        else:
            flash('Enter the text or choose file')

    user_id = None

    if username:
        user_id = get_user_info_by_login(username).id
        user_message = message_api.read_all_user_public_messages(user_id)
        user_message = message_manager.messages_organization(user_message, user_id)
        user_message.reverse()
    else:
        user_message = message_api.read_all_public_messages()
        user_message = message_manager.messages_organization(user_message)
        user_message = message_manager.sort_message(user_message)

    return render_template('public_messages.html',
                           public_messages=user_message,
                           user_id=user_id)


@app.route('/user/<username>', methods=['GET'])
def user(username):
    if request.method == 'GET':
        user = get_user_info_by_login(username)
        user_message = message_api.read_all_user_public_messages(user.id)
        user_message = message_manager.messages_organization(user_message, user.id)
        user_message.reverse()
        return render_template('public_messages.html',
                               public_messages=user_message)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if login and password:
            user = get_user_info_by_login(login)

            if user and check_password_hash(user.password, password):
                login_user(user)

                next_page = request.args.get('next')

                if not next_page:
                    next_page = '/'

                return redirect(next_page)
            else:
                flash('Login or password is not correct')
        else:
            flash('Please fill login and password fields')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        login = request.form.get('login')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if request.method == 'POST':
            if not (login or password or password2):
                flash('Please, fill all fields!')
            elif password != password2:
                flash('Passwords are not equal!')
            else:
                hash_pwd = generate_password_hash(password)
                new_user = User(login=login, password=hash_pwd)
                db.session.add(new_user)
                db.session.commit()

                return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response


def run():
    app.run(debug=True)
