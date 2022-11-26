import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request
from datetime import datetime

import numpy as np
from getData import *
from encryptPass import *
from createClub import *

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
    print('Found env file')
    
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg']) # allowed extensions for storing profile photos
UPLOAD_FOLDER = 'static/uploads/'
EXISTING_IDS = [] # to store all the existing user ids

# app configurations
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] ='0x67990'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Table for storing venue details
class venue_details(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name_of_venue = db.Column(db.String, unique=True, nullable=False)
    capacity = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.Integer, unique=False, nullable=False)

# Table to store transaction details
class transaction_details(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    sender = db.Column(db.String(300), unique=False, nullable=False)
    receiver = db.Column(db.String(300), unique=False, nullable=False)
    amount = db.Column(db.Float, unique=False, nullable=False)
    status = db.Column(db.Integer, unique=False, nullable=False)
    #time_started = db.Column(db.DateTime(200))
    #time_completed = db.Column(db.DateTime(200))
    #time_taken = db.Column(db.DateTime(200))

# Table to store feedback from user
class user_feedback(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)

class user_balance(db.Model):
    sn = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    user_name = db.Column(db.String, unique=False, nullable=False)
    balance = db.Column(db.Float, unique=False, nullable=False)

# Table to store the data for new events
class new_event(db.Model):
    sno = db.Column(db.Integer, autoincrement=True, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(200), unique=False)
    venue = db.Column(db.String(100), unique=False)
    start_d = db.Column(db.String(12), unique=False)
    end_d = db.Column(db.String(12), unique=False)
    no_parti = db.Column(db.Integer, unique=False)
    # spl_1 = db.Column(db.String(100), unique=False)
    # spl_2 = db.Column(db.String(100), unique=False)

db.create_all()


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# login using Auth0
@app.route("/login")
def login():
    
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )
    


# redirect to this page after successful authentication.
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    try:
        print('Trying to add new record')
        new_rec = user_balance(user_name=session.get('user')['userinfo']['name'], balance=10.0)
        db.session.add(new_rec)        
        db.session.commit()
    except:
        print('Could not add new record')
        
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/", methods=['GET', 'POST'])
def home():
    # temporary information
    if session:
        t = user_balance.query.filter_by(user_name=session.get('user')['userinfo']['name']).first()
        return render_template("home.html", session=session.get('user'), name=session.get('user')['userinfo']['name'],
            e=session.get('user')['userinfo']['email'],
            b=np.round(t.balance, 3), indent=4)
    else:
        return render_template("home.html", session=session.get('user'), indent=4)

# added new pages
# to send payments
@app.route('/payments', methods=['POST', 'GET'])
def payments():
    sender = ""
    if request.method == 'POST':
        sender = session.get('user')['userinfo']['name']
        # sender = request.form.get('senderName')
        receiver = request.form.get('receiverName')
        amt = float(request.form.get('amount'))
        print(sender, receiver, amt)

        # check if enogh balance is present with the sender
        c_user = user_balance.query.filter_by(user_name = sender).first()

        #print(f"{c_user.balance} : xxxx")
        if amt > 50:
            pass
            return "Insufficient balance"
        else:
            # query the sender receiver and update all records
            
            all_users = user_balance.query.order_by(user_balance.user_name).all()
            a_users = []

            # get details of all the users
            for u in all_users:
                a_users.append(u.user_name)
            #print(a_users)
            # merge records and delete records
            start_time = datetime.utcnow()
            #print(start_time)
            update_user = user_balance.query.filter_by(user_name = receiver).first()
            temp_bal = update_user.balance
            update_user_1 = user_balance.query.filter_by(user_name = receiver).first()
            update_user_1 = user_balance.query.filter_by(user_name = sender).first()
            temp_bal_1 = update_user_1.balance
            update_user.balance = temp_bal + amt
            #print(temp_bal)
            if temp_bal_1 < amt:
                return 'Insufficient balance.'
            if sender == receiver:
                return 'Invalid Transaction'
            update_sender = user_balance.query.filter_by(user_name = sender).first()
            temp_bal_1 = update_sender.balance
            update_sender.balance = temp_bal_1 - amt

            # update_user_1 = user_balance.query.filter_by(user_name = receiver).first()
            # temp_bal_1 = update_user_1.balance
            # update_user_1.balance = temp_bal_1 + amt
            # print(temp_bal_1)
            end_time = datetime.utcnow()
            
            # create a new valid transaction
            new_transaction = transaction_details(sender=getEncryptedUname(sender), receiver=getEncryptedUname(receiver), amount=amt, status=1)
            new_bal = user_balance(user_name=receiver, balance=amt)
            db.session.add(new_transaction)
            db.session.commit()
            return ('', 204)
    else:
        sender = session.get('user')['userinfo']['name']
        #print(sender)
        return render_template('payment.html', qr_url='../qr.png', senderName=sender)

# to receive payments
@app.route('/receive')
def receive():
    u =  session.get('user')['userinfo']['name']
    #print(u.name)
    return render_template('receive.html', uname=session.get('user')['userinfo']['name'], mail=session.get('user')['userinfo']['email'])

# view events
@app.route('/viewevent')
def viewevent():
    return render_template('viewevents.html')

# create new events
@app.route('/createvent', methods=['GET', 'POST'])
def createvent():
    if request.method == 'POST':
        f_name = request.form.get('full-name')
        des = request.form.get('description')
        venue = request.form.get('venue')
        s_d = request.form.get('Start_d')
        e_d = request.form.get('End_d')
        n = request.form.get('no_p')

        new_eve = new_event(full_name = f_name, desc = des, venue = venue, start_d = s_d, end_d = e_d, no_parti = n)
        try:
            db.session.add(new_eve)
            db.session.commit()
        except:
            print('Could not create an event')
        return render_template('payment.html')

    return render_template('createvent.html')

#club admin
@app.route('/clubadmin')
def clubadmin():
    return render_template('clubAdm.html')

# feedback
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        return render_template('feedback.html')
    else:
        # resp = request.form.get('feedback')
        # user_name = request.form.get('user-name')
        # email = request.form.get('user_email')
        # cur_today = datetime.datetime.now()
        #new_feedback = Usr_feedback(name=user_name, email=email, Feedback=resp, cur_date=cur_today)
        #db.session.add(new_feedback)
        #db.session.commit()
        return ('', 204)

@app.route('/rewards')
def rewards():
    return render_template('rewards.html')



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000), debug=True)