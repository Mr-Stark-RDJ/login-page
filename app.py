from flask import *
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)

userData = {}

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/home')
def home():
  return render_template('home.html',message=request.cookies.get('Token').title())



@app.route('/register',methods = ['POST', 'GET'])  
def register():
  if request.method == 'POST':
      username = request.form['username'].lower()  
      password = bcrypt.generate_password_hash(request.form['password']) 
      error=''
      if username in userData.keys():
        error='username already exit\n try new username'
        return render_template('signup.html',error=error)
      else:
        userData[username] = password 
        return redirect('/login')
  elif request.method == 'GET':
    return render_template('signup.html')
         

@app.route('/login',methods = ['POST','GET'])  
def login():  
  if request.method == "POST":  
    username = request.form['username'].lower()  
    password = request.form['password']
    if request.cookies.get('Token') == username:    
        return redirect('/home')
    else:
      print(f"{username} {password} {userData}")
      if username in userData.keys():
        print('working')
        if bcrypt.check_password_hash(userData[username], password) :
          print('working fine')
          resp = make_response(redirect('/home'))
          resp.set_cookie('Token',username)
          print('working smoothly')
          return resp
        else:
          return render_template('login.html',error="Wrong password")
      else:
        return render_template('login.html', error="Username doesn't exist")
  elif request.method == "GET":
    return render_template('login.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
