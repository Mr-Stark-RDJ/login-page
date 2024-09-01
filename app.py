from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.secret_key = b"s\x90\xfb\xa9\xf0\xdb\x18\x17\nJH+\xbe\x99K\xbar<\x08\x19uT'\xea"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)

    def __init__(self, username):
        this.username = username
        this.balance = 0.0

db.create_all()

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
    session['user_id'] = user.id
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/add_balance', methods=['POST'])
def add_balance():
    user_id = session.get('user_id')
    amount = request.form.get('amount')
    
    if not user_id or not amount:
        return jsonify({'error': 'Invalid input'}), 400
    
    api_key = '0DQNMVQ-GD3MDJ1-Q41F3AQ-RVPYZHV' 
    payload = {
        'price_amount': amount,
        'price_currency': 'usd',
        'pay_currency': 'btc',
        'ipn_callback_url': 'https://login.up.railway.app/payment_callback', 
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
    app.run(debug=True)
