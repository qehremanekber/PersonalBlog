import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, Response
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.exceptions import abort

from forms import LoginForm, RegisterForm

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.debug = True
app.config['SECRET_KEY'] = 'your secret key'

login_manager = LoginManager(app)
login_manager.login_view = "login"


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password
        self.authenticated = False

    def is_active(self):
        return self.is_active()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    curs = conn.cursor()
    curs.execute("SELECT * from users where user_id = (?)", [user_id])
    lu = curs.fetchone()
    if lu is None:
        return None
    else:
        return User(int(lu[0]), lu[1], lu[6])


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    # user_id = current_user.get_id()

    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>', methods=('GET', 'POST'))
def post(post_id):
    post = get_post(post_id)
    conn = get_db_connection()
    fk = conn.execute("SELECT * FROM posts WHERE id=(?)", [post_id]).fetchone()
    user = conn.execute("SELECT * FROM users WHERE user_id=(?)", [fk[4]]).fetchone()
    if request.method == 'POST':
        comment_content = request.form['comment_content']
        user_id = current_user.get_id()

        conn.execute('INSERT INTO comments (ccontent, user2, posted) VALUES (?, ?, ?)',
                     (comment_content, user_id, post_id))

        conn.commit()
        #conn.close()

    content2 = conn.execute("SELECT * FROM comments WHERE posted=(?)",
                            [post_id]).fetchall()

    return render_template('post.html', post=post, user=user, fk=fk, content2=content2)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = current_user.get_id()

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content, user1) VALUES (?, ?,?)',
                         (title, content, user_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


# @app.route('/<int:post_id>', methods=('GET', 'POST'))
# def comment():
#     if request.method == 'POST':
#         comment_content = request.form['comment_content']
#         user_id = current_user.get_id()
#
#         if not comment_content:
#             flash('Content is required!')
#         else:
#             conn = get_db_connection()
#             conn.execute('INSERT INTO comments (ccontent, user2) VALUES (?, ?)',
#                          (comment_content, user_id))
#             conn.commit()
#             conn.close()
#
#     return render_template('post.html')


#
# @app.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         name = request.form['name']
#         surname = request.form['surname']
#         username = request.form['username']
#         password = request.form['password']
# 
#         if not username:
#             flash('Username is Required')
#         if not password:
#             flash('Password is Required')
#         if not name:
#             flash('First Name is Required')
#         if not surname:
#             flash('Last Name is Required')
#         else:
#             conn = get_db_connection()
#             conn.execute('INSERT INTO users (name,surname,username,password) VALUES (?, ?, ?, ?)',
#                          (name, surname, username, password))
#             conn.commit()
#             conn.close()
#             return redirect(url_for('index'))
# 
#     return render_template('register.html')


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        curs = conn.cursor()
        hashed = bcrypt.generate_password_hash(form.password1.data).decode('utf-8')
        curs.execute("INSERT INTO users(email, name, surname, username, gender, password) VALUES (?, ?, ?, ?, ?, ?)",
                     (form.email.data, form.name.data, form.surname.data, form.username.data, form.gender.data,
                      hashed))

        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        curs = conn.cursor()
        curs.execute("SELECT * FROM users where email = (?)", [form.email.data])
        user = list(curs.fetchone())
        Us = load_user(user[0])
        if form.email.data == Us.email and bcrypt.check_password_hash(Us.password, form.password.data):
            login_user(Us, remember=form.remember.data)
            flash('Logged in successfully')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessfull.')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
