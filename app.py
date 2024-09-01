from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)
app.secret_key = b"s\x90\xfb\xa9\xf0\xdb\x18\x17\nJH+\xbe\x99K\xbar<\x08\x19uT'\xea"

# Configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)  # Adding a password field
    balance = db.Column(db.Float, default=0.0)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.balance = 0.0

# Create database tables within the application context
with app.app_context():
    db.create_all()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return "User already exists! Try logging in."
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return "Invalid username or password!"
    return render_template('login.html')

# Dashboard route to display user balance
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

# Route to initiate payment
@app.route('/add_balance', methods=['POST'])
def add_balance():
    user_id = session.get('user_id')
    amount = request.form.get('amount')
    
    if not user_id or not amount:
        return jsonify({'error': 'Invalid input'}), 400
    
    api_key = 'YOUR_NOWPAYMENTS_API_KEY'  # Replace with your actual NOWPayments API key
    payload = {
        'price_amount': amount,
        'price_currency': 'usd',
        'pay_currency': 'btc',
        'ipn_callback_url': 'https://login.up.railway.app/payment_callback',  # Using your live URL
        'order_id': user_id,
        'order_description': 'Add Balance'
    }

    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.post('https://api.nowpayments.io/v1/invoice', json=payload, headers=headers)
    data = response.json()

    if response.status_code == 200:
        return redirect(data['invoice_url'])
    else:
        return jsonify({'error': 'Payment initiation failed'}), 500

# Route to handle payment callback
@app.route('/payment_callback', methods=['POST'])
def payment_callback():
    payment_status = request.json.get('payment_status')
    user_id = request.json.get('order_id')
    amount = request.json.get('pay_amount')

    if payment_status == 'confirmed':
        update_user_balance(user_id, amount)
        return jsonify({'message': 'Balance updated successfully'}), 200
    else:
        return jsonify({'error': 'Payment not confirmed'}), 400

def update_user_balance(user_id, amount):
    user = User.query.get(user_id)
    if user:
        user.balance += float(amount)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
