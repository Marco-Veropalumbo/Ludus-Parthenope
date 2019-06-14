from flask import Flask, render_template, url_for, session, request, redirect
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb+srv://Marco:Password1@ludus-parthenope-u9h85.mongodb.net/Ludus-Parthenope?retryWrites=true&w=majority"
mongo = PyMongo(app);

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))

    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pw'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return 'Username o password errati'

@app.route('/logout')
def logout():
   session.pop('username', None)
   return redirect(url_for('index'))

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username'] })

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pw'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return 'Esiste gi&agrave; un utente con questo username!'

    return render_template('register.html')

@app.route('/home')
def home():
    if 'username' in session:
        session.database = mongo.db
        return render_template('home.html')

    else:
        return redirect(url_for('index'))

@app.route('/library')
def library():
    if 'username' in session:
        session.database = mongo.db
        return render_template('library.html')

    else:
        return redirect(url_for('index'))

@app.route('/join/<torneo>')
def join(torneo):
    mongo.db.tournaments.update_one({'name': torneo}, {"$addToSet": {'competitors': session['username']}})
    return redirect(url_for('home'))

@app.route('/aggiungi',methods=['POST'])
def aggiungi():
    newgame = request.form['add']
    mongo.db.users.update_one({'name': session['username'] }, {"$addToSet": {'games': newgame}})
    return redirect(url_for('library'))


if __name__ == '__main__':
    app.run()
app.secret_key = 'super secret key'
