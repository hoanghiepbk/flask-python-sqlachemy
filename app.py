from flask import Flask, session, render_template, redirect, url_for, request, flash

from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm 

from wtforms import StringField, PasswordField, BooleanField, ValidationError

from wtforms.validators import InputRequired, Email, Length

from flask_sqlalchemy  import SQLAlchemy

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

from flask.ext.login import current_user

from sqlalchemy.orm import relationship, backref

import os







app = Flask(__name__)





app.config['SECRET_KEY'] = 'kmapydev'

db_path = os.path.join(os.path.dirname(__file__), 'database.db')

db_uri = 'sqlite:///{}'.format(db_path)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri



Bootstrap(app)

db = SQLAlchemy(app)

login_manager = LoginManager()

login_manager.init_app(app)

class User(UserMixin,db.Model):

    __tablename__ = "user"

    id = db.Column('id',db.Integer, primary_key=True)

    username = db.Column(db.String(15), unique=True)

    email = db.Column(db.String(50), unique=True)

    password = db.Column(db.String(80))



    book = db.relationship('Book', backref='owner', lazy='dynamic')

 

@login_manager.user_loader

def load_user(user_id):

    return User.query.get(int(user_id))



class LoginForm(FlaskForm):

    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])

    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

    remember = BooleanField('remember me')



class RegisterForm(FlaskForm):

    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])

    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])

    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])



    def validate_email(self, field):

        if User.query.filter_by(email=field.data).first():

            raise ValidationError('Email is already in use.')



    def validate_username(self, field):

        if User.query.filter_by(username=field.data).first():

            raise ValidationError('Username is already in use.')



class Book(db.Model):

    __tablename__ = "book"

    id = db.Column('id',db.Integer, primary_key=True)

    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #book_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)

    #userR = db.relationship('User', foreign_keys='Book.user_id')

    #bookR = db.relationship('User', foreign_keys='Book.book_id')

    title = db.Column(db.String(50), unique=True)

    author = db.Column(db.String(20))

    price = db.Column(db.String(10))

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))





class CreateForm(FlaskForm):

    title = StringField('title', validators=[InputRequired(), Length(min=1, max=50)])

    author = StringField('author', validators=[InputRequired(), Length(min=1, max=25)])

    price = StringField('price', validators=[InputRequired(), Length(min=4, max=10)])





@app.route('/')

def index():

    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])

def login():

    form = LoginForm()



    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user is not None and user.password == form.password.data:

            login_user(user)

            return redirect(url_for('dashboard'))

        else:

            flash('Invalid username or password.')

    return render_template('login.html', form=form)



@app.route('/register', methods=['GET', 'POST'])

def register():

    form = RegisterForm()



    if form.validate_on_submit():

        user = User(username=form.username.data, email=form.email.data, password=form.password.data)

        db.session.add(user)

        db.session.commit()

        flash('You have successfully registered! You may now login.')

        return redirect(url_for('login'))





    return render_template('register.html', form=form)



@app.route('/logout')

@login_required

def logout():

    logout_user()

    flash('You have successfully been logged out.')



    return redirect(url_for('login'))



@app.route('/dashboard')

def dashboard():

    return render_template('dashboard.html')



@app.route('/dashboard/create', methods=['GET','POST'])

def create():

    form = CreateForm()

    if form.validate_on_submit():



        new_book = Book(title=form.title.data, author=form.author.data, price=form.price.data)

        db.session.add(new_book)

        db.session.commit()

        flash('You have successfully create book')

    return render_template('create.html', form=form)



@app.route('/create/show', methods=['GET','POST'])

def show():

    #userID = session['user_id']

    #books = User.query.join(Book, user.id == book.owner_id).filter(book.owner_id == userID).order_by(Book.title.desc(),Book.author.desc(),Book.price.desc())

    

    return render_template(
        'result.html',

        #books = Book.query.all())

        books = User.query.join(Book).order_by(Book.title.desc(),Book.author.desc(),Book.price.desc()))

    

    #return render_template('result.html', books=books)



@app.route("/show", methods=["POST"])

def update():

    newtitle = request.form.get("newtitle")

    oldtitle = request.form.get("oldtitle")

    newauthor = request.form.get("newauthor")

    oldauthor = request.form.get("oldauthor")

    newprice = request.form.get("newprice")

    oldprice = request.form.get("oldprice")

    book = Book.query.filter_by(title=oldtitle,author=oldauthor,price=oldprice).first()

    book.title = newtitle

    book.author = newauthor

    book.price = newprice

    db.session.commit()

    

    return '<h2>Update success</h2>'



@app.route("/", methods=["POST"])

def delete():

    title = request.form.get("title")

    author = request.form.get("author")

    price = request.form.get("price")

    book = Book.query.filter_by(title=title,author=author,price=price).first()

    db.session.delete(book)

    db.session.commit()





if __name__ == '__main__':

    app.run()
