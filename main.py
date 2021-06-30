from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from random import shuffle
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from dotenv import load_dotenv
import os
from forms import RegisterForm, LoginForm
from flask_wtf import FlaskForm
from wtforms import SubmitField


load_dotenv()

art_list = ["about.png", "boat.png", "bus.png", "elephantus.png", "gojongarr.png", "hana.png", "hula.png", "lenny.png", "leonard.png", "paradies.png", "station.png", "the_handbag.png", "this_is_the_way.png", "zowie.png"]
art_path_list = [f"static/images/art/{a}" for a in art_list]
title_list = ["I'm about to tell you...", "The Boat House", "The Bus Gang", "Elegypt", "Dr. Gojongarr was an incredibly nice man", "Hana no Koala", "Hula Horse", "The Ballad of Lenny Kowalusky and the Man Sized Critter", "Leonard", "The Catcher of Birds of Paradise", "The Station Master", "The Handbag of the Best Friend of the Boy Who Has the Whole Universe Inside his Mouth", "This is the way we make the sun rise", "Zowie-Kerpowie"]
description_list = ["2021, Oil on Canvas, 100x80cm"]
price_list = ["1000", "1000", "1500", "2500", "2000", "2500", "1000", "2000", "2500", "1500", "1000", "3500", "2500", "1500"]

# shuffle(art_path_list)
# print(art_path_list)
now = datetime.now()
current_year = now.strftime("%Y")

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artworks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("APP_SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)



class Artwork(db.Model):
    __tablename__ = "artworks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    price = db.Column(db.String(250), nullable=True)
    sold = db.Column(db.Boolean, nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    bought = relationship("Purchase", back_populates="buyer")

class Purchase(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey('users.id'))
    buyer = relationship("User", back_populates="bought")





# db.create_all()


def create_art_database():
    for a in range(len(art_list)):
        new_artwork = Artwork(
            title=title_list[a],
            description="2021, Oil on Canvas, 100x80cm",
            img_url=art_path_list[a],
            price=price_list[a],
            sold=False
        )
        db.session.add(new_artwork)
        db.session.commit()

# create_art_database()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        art_id = request.form.get('buy-button')
        artwork = Artwork.query.get(art_id)
        artwork.sold = True
        new_purchase = Purchase(
            id=art_id
            )
        db.session.add(new_purchase)
        db.session.commit()
    purchases = Purchase.query.count()
    all_artworks = Artwork.query.all()
    art_list = []
    for artwork in all_artworks:
        if not artwork.sold:
            art_list.append(artwork)
    shuffle(art_list)
    return render_template("index.html", art_list=art_list, purchases=purchases, current_year=current_year)


@app.route('/cart', methods=['POST', 'GET'])
def cart():
    if request.method == 'POST':
        art_id = request.form.get('remove-button')
        Purchase.query.filter_by(id=art_id).delete()
        artwork = Artwork.query.get(art_id)
        artwork.sold = False
        db.session.commit()
    purchases = Purchase.query.count()
    all_purchases = Purchase.query.all()
    purchase_id_list = []
    purchases_list = []
    for purchase in all_purchases:
        purchase_id_list.append(purchase.id)
        purchases_list.append(Artwork.query.get(purchase.id))
    # print(purchase_id_list)
    # for art in purchases_list:
    #     print(art.title)
    # return redirect(url_for('home'))
    return render_template("cart.html", purchases_list=purchases_list, purchases=purchases, current_year=current_year)


@app.route('/register', methods=['POST', 'GET'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            flash('You are already registered. Please log-in instead.')
            return redirect(url_for('login'))
        password = register_form.password.data
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(email=register_form.email.data, password=hashed_password, name=register_form.name.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        if Purchase.query.count() > 0:
            return redirect(url_for("cart"))
        else:
            return redirect(url_for("home"))
    return render_template("register.html", form=register_form, current_year=current_year)

@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if not user:
            flash('That email is not valid. Please try again.')
            return redirect(url_for('login'))
        login_password = login_form.password.data
        password_check = check_password_hash(user.password, login_password)
        if not password_check:
            flash('Password incorrect. Please try again.')
            return redirect(url_for('login'))
        if password_check:
            login_user(user)
            print(user.is_authenticated)
            if Purchase.query.count() > 0:
                return redirect(url_for("cart"))
            else:
                return redirect(url_for('home'))
    return render_template("login.html", form=login_form, current_year=current_year)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('home'))



if __name__ == "__main__":
	app.run(debug=True)
