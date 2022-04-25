import datetime
import time
from operator import and_

import jinja2
from flask import Flask, render_template, redirect, url_for, request
from flask_login import login_required, current_user, login_user, logout_user
from humanize import naturaltime

from models.User import login, User, Note
from models.User import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://alex:test@192.168.193.132/note?client_encoding=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'xyz'
db.init_app(app)
login.init_app(app)
login.login_view = "login"


@app.template_filter()
def humanize_timestamp(date_time_obj):
    return naturaltime(datetime.datetime.now() - date_time_obj)


@app.before_first_request
def create_table():
    db.create_all()


@app.route('/')
def index():
    notes = None
    if current_user.is_authenticated:
        user_id = current_user.id
        notes = Note.query.filter(
            Note.user_id == user_id
        ).all()
    return render_template("index.html.jinja2", notes=notes)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            return render_template("login.html.jinja2")
    return render_template("login.html.jinja2")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        first_name = request.form["fname"]
        last_name = request.form["lname"]
        email = request.form["email"]
        password = request.form["password"]

        if not User.query.filter_by(email=email).first():
            user = User(email=email, first_name=first_name, last_name=last_name, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("signup.html.jinja2")


@app.route('/introduction', methods=['POST', 'GET'])
def introduction():
    return render_template("introduction.html.jinja2")


@app.route('/note/new', methods=['POST', 'GET'])
@login_required
def new_note():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]

        note = Note(title=title, body=body, user_id=current_user.id)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("new.html.jinja2")


@app.route('/note/view/<int:id>', methods=['GET'])
@login_required
def view_note(id: int):
    user_id = current_user.id
    note = Note.query.filter(
        and_(Note.user_id == user_id, Note.id == id)
    ).one()
    return render_template("view.html.jinja2", note=note)


@app.route('/note/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_note(id: int):
    user_id = current_user.id
    note = Note.query.filter(
        and_(Note.user_id == user_id, Note.id == id)
    ).one()
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        note.title = title
        note.body = body
        db.session.commit()
    if request.method == "GET":
        return render_template("edit.html.jinja2", note=note)
    return redirect(url_for("index"))


@app.route('/note/delete/<int:id>', methods=['DELETE', 'GET'])
@login_required
def delete_note(id: int):
    if request.method == "DELETE":
        user_id = current_user.id
        note = Note.query.filter(
            and_(Note.user_id == user_id, Note.id == id)
        ).one()
        db.session.delete(note)
        db.session.commit()
    return "Deleted Note"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run()
