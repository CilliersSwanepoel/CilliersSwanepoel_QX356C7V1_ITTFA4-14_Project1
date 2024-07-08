from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from datetime import datetime
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Quxub7164*02@localhost/Users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_data.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

    def __init__(self, game_id, user_id, content):
        self.game_id = game_id
        self.user_id = user_id
        self.content = content

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

stores_url = 'https://www.cheapshark.com/api/1.0/stores'
stores_response = requests.get(stores_url)
stores_data = stores_response.json()

store_dict = {store['storeID']: store['storeName'] for store in stores_data}

store_links = {
    "1": "https://www.winstore.com",
    "2": "https://www.dlgamer.com",
    "3": "https://www.gamebillet.com",
    "4": "https://www.dreamgame.com",
    "5": "https://www.2game.com",
    "6": "https://www.gamesplanet.com",
    "7": "https://www.greenmangaming.com",
    "8": "https://www.gamersgate.com",
    "9": "https://www.humblebundle.com/store",
    "10": "https://www.fanatical.com",
    "11": "https://www.gamesload.com",
    "12": "https://www.indiegala.com"
}

@app.route('/game_deals')
def game_deals():
    deals_url = "http://www.cheapshark.com/api/1.0/deals"
    deals_response = requests.get(deals_url)

    if deals_response.status_code == 200:
        deals = deals_response.json()
    else:
        deals = []

    return render_template('game_deals.html', deals=deals, stores=store_dict)

@app.route('/game/<game_id>', methods=['GET', 'POST'])
def game_item_view(game_id):
    print(f"Received game_id: {game_id}")  # Debug statement
    response = requests.get(f"http://www.cheapshark.com/api/1.0/games?id={game_id}")
    if response.status_code != 200:
        flash('Failed to fetch game details.', 'danger')
        return redirect(url_for('home'))

    game = response.json()
    print(f"Game details: {game}")  # Debug statement

    # Fetch comments for this game
    comments = Comment.query.filter_by(game_id=game_id).order_by(Comment.timestamp.desc()).all()
    print(f"Comments: {comments}")  # Debug statement

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need to be logged in to post a comment.', 'danger')
            return redirect(url_for('login'))
        
        content = request.form['content']
        print(f"Form content: {content}")  # Debug statement
        comment = Comment(game_id=game_id, user_id=current_user.id, content=content)
        db.session.add(comment)
        db.session.commit()
        print(f"Comment added: {comment}")  # Debug statement
        flash('Comment posted successfully!', 'success')
        return redirect(url_for('game_item_view', game_id=game_id))
    
    return render_template('game_item_view.html', game=game, store_dict=store_dict, store_links=store_links, comments=comments, game_id=game_id)

@app.route('/protected')
@login_required
def protected():
    return "This is a protected route."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
