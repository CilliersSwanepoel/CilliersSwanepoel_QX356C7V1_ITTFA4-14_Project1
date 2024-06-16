from flask import Flask, render_template, request, redirect, url_for, flash, abort
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.urandom(24)  # In production, use a fixed secret key stored securely
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Quxub7164*02@localhost/Users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, surname=surname, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=request.form.get('remember'))
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Fetch and cache store information
stores_url = 'https://www.cheapshark.com/api/1.0/stores'
stores_response = requests.get(stores_url)
stores_data = stores_response.json()

# Create a dictionary to map storeID to store name
store_dict = {store['storeID']: store['storeName'] for store in stores_data}

@app.route('/game_deals')
def game_deals():
    # Fetch game deals from CheapShark API
    deals_url = "http://www.cheapshark.com/api/1.0/deals"
    deals_response = requests.get(deals_url)

    if deals_response.status_code == 200:
        deals = deals_response.json()
    else:
        deals = []

    return render_template('game_deals.html', deals=deals, stores=store_dict)

@app.route('/game/<game_id>')
def game_item_view(game_id):
    # Fetch game details from CheapShark API
    response = requests.get(f"http://www.cheapshark.com/api/1.0/games?id={game_id}")
    game = response.json()
    # Debug statement to check game_id
    print(f"Fetched game details for game_id: {game_id}")
    return render_template('game_item_view.html', game=game, store_dict=store_dict)

# Example of a protected route
@app.route('/protected')
@login_required
def protected():
    return "This is a protected route."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
