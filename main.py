from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from random import shuffle
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from dotenv import load_dotenv
import os
import stripe
from forms import RegisterForm, LoginForm


# load environment variables
load_dotenv()
stripe.api_key=os.getenv("STRIPE_API_KEY")
# For maintaining year for copyright notice.
now = datetime.now()
current_year = now.strftime("%Y")
checkout_price = 0
# For initializing artworks database
# art_list = ["about.png", "boat.png", "bus.png", "elephantus.png", "gojongarr.png", "hana.png", "hula.png", "lenny.png", "leonard.png", "paradies.png", "station.png", "the_handbag.png", "this_is_the_way.png", "zowie.png"]
# art_path_list = [f"static/images/art/{a}" for a in art_list]
# title_list = ["I'm about to tell you...", "The Boat House", "The Bus Gang", "Elegypt", "Dr. Gojongarr was an incredibly nice man", "Hana no Koala", "Hula Horse", "The Ballad of Lenny Kowalusky and the Man Sized Critter", "Leonard", "The Catcher of Birds of Paradise", "The Station Master", "The Handbag of the Best Friend of the Boy Who Has the Whole Universe Inside his Mouth", "This is the way we make the sun rise", "Zowie-Kerpowie"]
# description_list = ["2021, Oil on Canvas, 100x80cm"]
# price_list = ["1000", "1000", "1500", "2500", "2000", "2500", "1000", "2000", "2500", "1500", "1000", "3500", "2500", "1500"]

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


app = Flask(__name__)
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artworks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("APP_SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

# Database models
class Artwork(db.Model):
    __tablename__ = "artworks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    price = db.Column(db.String(250), nullable=True)
    sold = db.Column(db.Boolean, nullable=False)
    buyer_id = Column(Integer, ForeignKey('users.id'))
    buyer = relationship("User", back_populates="bought")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    reserved = relationship("Purchase", back_populates="buyer")
    bought = relationship("Artwork", back_populates="buyer")


class Purchase(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True)
    product_id = Column(db.Integer)
    buyer_id = Column(Integer, ForeignKey('users.id'))
    buyer = relationship("User", back_populates="reserved")




# Initialize database
# db.create_all()

# Populate artwork stock
# create_art_database()

# Updates cart items, from pre-login state, upon login
def update_user_purchases():
    all_purchases = Purchase.query.all()
    # iterate through purchase table and any items
    # without buyer-id set to current user id
    for purchase in all_purchases:
        if not purchase.buyer_id:
            purchase.buyer_id = current_user.get_id()
            db.session.commit()


def get_purchase_count():
    # returns amount of items in a non-logged-in cart
    purchases = 0
    all_purchases = Purchase.query.all()
    for purchase in all_purchases:
        if not purchase.buyer_id:
            purchases += 1
    return purchases

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        # get artwork id passed from button
        art_id = request.form.get('buy-button')
        if current_user.is_authenticated:
            new_purchase = Purchase(
                product_id=art_id,
                buyer_id=current_user.get_id()
            )
        else:
            new_purchase = Purchase(
                product_id=art_id
                )
        db.session.add(new_purchase)
        db.session.commit()
    list_of_art = []
    art_id_list = []
    purchases = 0
    all_purchases = Purchase.query.all()
    for purchase in all_purchases:
        # if user is logged-in, append only artworks not in
        # their shopping cart so that only these render in home page
        if current_user.is_authenticated:
            if purchase.buyer_id == int(current_user.get_id()):
                art_id_list.append(purchase.product_id)
                purchases += 1
        # if nobody is logged in, only append the artworks which
        # do not have a buyer id, as these are the only ones in
        # the non-logged-in cart
        else:
            if not purchase.buyer_id:
                art_id_list.append(purchase.product_id)
                purchases += 1
    # create list of unique ids of artworks not to
    # include in the home page render
    art_id_list = list(set(art_id_list))
    all_artworks = Artwork.query.all()
    # create list of artworks which are not in the exclude list
    for artwork in all_artworks:
        if artwork.id not in art_id_list:
            list_of_art.append(artwork)
    # list comprehension, only art which is not sold should be rendered.
    final_art_list = [art for art in list_of_art if not art.sold]
    # shuffle, so that each new render presents art in different order
    shuffle(final_art_list)
    return render_template("index.html", art_list=final_art_list, purchases=purchases, current_year=current_year)


@app.route('/cart', methods=['POST', 'GET'])
def cart():
    global checkout_price
    # delete unwanted artworks from cart
    if request.method == 'POST':
        # get id for artwork-to-remove, passed by the button
        art_id = request.form.get('remove-button')
        # delete the instance of the artwork which has relationship with logged-in user
        if current_user.is_authenticated:
            Purchase.query.filter_by(product_id=art_id).filter_by(buyer_id=current_user.get_id()).delete()
        # otherwise, if not logged-in just delete temporarily stored instance
        else:
            Purchase.query.filter(Purchase.product_id == art_id).filter(Purchase.buyer_id == None).delete()
        db.session.commit()
    all_purchases = Purchase.query.all()
    purchase_id_list = []
    purchases_list = []
    # iterate through purchases table
    for purchase in all_purchases:
        if current_user.is_authenticated:
            # if a user is logged in, gather only the artworks
            # linked to the current user, for rendering in the cart, and increment checkout price
            if purchase.buyer_id == int(current_user.get_id()):
                purchase_id_list.append(purchase.product_id)
                artwork = Artwork.query.get(purchase.product_id)
                purchases_list.append(artwork)
                checkout_price += int(float(artwork.price) * 100)
        # otherwise only render the items without a buyer id
        else:
            if not purchase.buyer_id:
                purchase_id_list.append(purchase.product_id)
                purchases_list.append(Artwork.query.get(purchase.product_id))
    return render_template("cart.html", purchases_list=purchases_list, purchases=len(purchases_list), current_year=current_year)


@app.route('/register', methods=['POST', 'GET'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data
        # check if user already exists
        user = User.query.filter_by(email=email).first()
        # if so, flash message and redirect to login
        if user:
            flash('You are already registered. Please log-in instead.')
            return redirect(url_for('login'))
        # otherwise, hash password and create new user
        password = register_form.password.data
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(email=register_form.email.data, password=hashed_password, name=register_form.name.data)
        db.session.add(new_user)
        db.session.commit()
        # login user
        login_user(new_user)
        # add any items that were in the cart before login,
        # to the user's items in the purchase table
        update_user_purchases()
        # if items in users cart, redirect to cart
        if Purchase.query.filter(Purchase.buyer_id == current_user.get_id()).count() > 0:
            return redirect(url_for("cart"))
        # otherwise, redirect to home
        else:
            return redirect(url_for("home"))
    purchases = get_purchase_count()
    return render_template("register.html", form=register_form, purchases=purchases, current_year=current_year)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        # check if user exists in database, if not, redirect to try again
        if not user:
            flash('That email is not valid. Please try again.')
            return redirect(url_for('login'))
        # compare entered password with stored password
        login_password = login_form.password.data
        password_check = check_password_hash(user.password, login_password)
        # redirect for wrong password
        if not password_check:
            flash('Password incorrect. Please try again.')
            return redirect(url_for('login'))
        if password_check:
            login_user(user)
            # add any cart items from pre-login, to users cart
            update_user_purchases()
            if Purchase.query.count() > 0:
                return redirect(url_for("cart"))
            else:
                return redirect(url_for('home'))
    purchases = get_purchase_count()
    return render_template("login.html", form=login_form, purchases=purchases, current_year=current_year)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    all_purchases = Purchase.query.all()
    for purchase in all_purchases:
        # delete all items from purchase table which don't have buyer
        if not purchase.buyer_id:
            Purchase.query.filter_by(id=purchase.id).delete()
            db.session.commit()
    logout_user()
    return redirect(url_for('home'))


@app.route('/cancel', methods=['GET'])
def cancel():
    global checkout_price
    # reset checkout price
    checkout_price = 0
    # set purchases amount for cart icon counter display
    purchases = 0
    all_purchases = Purchase.query.all()
    for purchase in all_purchases:
        if purchase.buyer_id == int(current_user.get_id()):
            purchases += 1
    return render_template("cancel.html", purchases=purchases, current_year=current_year)

@app.route('/success', methods=['GET'])
def success():
    global checkout_price
    # after successful checkout, clear cart and total
    checkout_price = 0
    user_id_as_int = int(current_user.get_id())
    # reset purchases count for cart icon display
    purchases = 0
    all_purchases = Purchase.query.all()
    for purchase in all_purchases:
        if purchase.buyer_id == user_id_as_int:
            # set all bought artworks to 'Sold', and set buyer_id to the sold artwork
            artwork = Artwork.query.get(purchase.product_id)
            artwork.sold = True
            artwork.buyer_id = str(user_id_as_int)
            # delete bought artwork from buyers cart
            Purchase.query.filter_by(id=purchase.id).delete()
    db.session.commit()
    return render_template("success.html", purchases=purchases, current_year=current_year)

# Stripe checkout session
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    global checkout_price
    # generate success and cancel paths
    success_url = os.path.join(request.url_root, 'success')
    cancel_url = os.path.join(request.url_root, 'cancel')
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': checkout_price,
                        'product_data': {
                            'name': 'Artwork from Ātoshoppu',
                            'images': ['static/images/art/atoshoppu_logo.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403


if __name__ == "__main__":
    app.run(debug=True)


