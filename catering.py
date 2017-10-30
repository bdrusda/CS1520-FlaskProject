import os
import hashlib
from datetime import date , datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask import Flask, render_template, request
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catering.db'

db = SQLAlchemy(app)

owner_username = 'owner'
owner_password = 'pass'


class User(db.Model):
    id = db.Column(db.String, primary_key=True , unique=True)
    user = db.Column(db.String(80))
    password = db.Column(db.String(120), nullable=False)

    permissions = db.Column(db.String(50), nullable=False)


class Events(db.Model):
    creator = db.Column(
        db.String,
        nullable=False)  # creator of event by ID number
    staff = db.Column(db.String , nullable=True)  # Staff working any given a
    staff2 = db.Column(db.String , nullable=True)
    staff3 = db.Column(db.String , nullable=True)
    Date = db.Column(db.DateTime, nullable=False , primary_key=True)


@app.route("/", methods=['GET', 'POST'])
def render_index():
    return render_template('index.html')

@app.route('/go_to_event/', methods=['GET', 'POST'])
def render_events():
    return render_template('create_event.html')

@app.route('/signup/', methods=['GET', 'POST'])
def handle_signup():
    return render_template('signup.html')

@app.route('/staff_signup/' , methods= ['GET' , 'POST'])
def get_staff_create(): 
    return render_template('staff_signup.html')

@app.route('/login/', methods=['GET', 'POST'])
def handle_login():

    password1 = request.form['password']
    username = request.form['username']

    m = hashlib.md5(password1.encode('utf-8')).hexdigest()
    crypt_pass = str(m)

    value = User.query.filter_by(id=str(crypt_pass)).first()

    permissions = value.permissions

    if value is None:
        return render_template('index.html')

    elif permissions == 'owner':
        
        all_events = Events.query.all()
        
        return render_template(
            'login.html',
            username=username,
            permissions=permissions,
            all_events=all_events)

    elif permissions == 'std':
        
        events = Events.query.filter_by(creator=username).all()

        return render_template(
            'login.html',
            username=username,
            permissions=permissions,
            events = events)

    elif permissions == 'staff':
        
        q1 = Events.query.filter_by(staff = username).all()
        q2 = Events.query.filter_by(staff2 = username).all()
        q3 = Events.query.filter_by(staff3 = username).all()

        query = q1 + q2 + q3
    
        not_full = Events.query.all()
        
        for values in not_full: 
            if values.staff == username or values.staff2 == username or values.staff3 == username:
                not_full.remove(values)

        for events in not_full: 
            if events.staff != None and events.staff2 != None and events.staff3 != None: 
                not_full.remove(events)


        return render_template(
                'login.html',
                username = username,
                permissions = permissions,
                query = query,
                not_full = not_full
                )


@app.route('/push_staff/', methods=['GET', 'POST'])
def handle_staff_signup():
    username = request.args.get('username' , None)
    password = request.args.get('password' , None)

    m = hashlib.md5(password.encode('utf-8')).hexdigest()

    crypt_pass = str(m)

    user = User(
            id = str(crypt_pass),
            user = username,
            password = password,
            permissions = 'staff'
            )
    
    db.session.add(user)
    db.session.commit()
       
    all_events = Events.query.all()

    return render_template(
            'login.html',
            username='owner',
            all_events = all_events,
            permissions = 'owner')

@app.route('/add_event/', methods=['GET', 'POST'])
def handle_add_event():
    error = False
    username = request.args.get('creator' , None)
    date = request.args.get('date', None)
    password = request.args.get('password' , None)   
    final_date = make_date(date) 

    m = hashlib.md5(password.encode('utf-8')).hexdigest()
    crypt_pass = str(m)
    
    value = User.query.filter_by(id=str(crypt_pass)).first()

    event = Events(creator=username, Date=final_date)
    
    try:
        db.session.add(event)
        db.session.commit()
    except exc.IntegrityError: 
        db.session.rollback()
        error = True

    events = Events.query.filter_by(creator=username).all()

    if value == None or error == True: 
        return render_template('create_event.html' , error=True)
    else: 
        return render_template(
                'login.html',
                username=username,
                events = events,
                permissions = 'std'
                )


@app.route('/handle_signup/', methods=['GET', 'POST'])
def add_std_user():

    username = request.form['username']
    password = request.form['password']
    m = hashlib.md5(password.encode('utf-8')).hexdigest()
    
    crypt_pass = str(m)

    user = User(
        id=str(crypt_pass),
        user=username,
        password=password,
        permissions='std')
    db.session.add(user)
    db.session.commit()

    return render_template('index.html')

@app.route('/delete_event/' , methods=['GET' , 'POST'])
def delete_event(): 
    date = request.form['delete_event']
    username = request.form['username']
    values = date[8:]
    
    to_delete = make_date(values)

    data_obj =Events.query.filter_by(Date=to_delete).first()
    
    db.session.delete(data_obj)
    db.session.commit()
    
    events = Events.query.filter_by(creator=username).all()

    return render_template(
            'login.html',
            username=username,
            events = events,
            permissions = "std"
            )

@app.route('/add_staff/' , methods = ['GET' , 'POST'])  
def add_staff_events(): 
    username = request.form['username']
    event_date = request.form['add_staff']
    
    value = event_date[6:]
    data = make_date(value)

    event = Events.query.filter_by(Date=data).first()

    if event.staff == None and event.staff != username: 
        event.staff = username
        
    elif event.staff2 == None and event.staff2 != username:
        event.staff2 = username
    
    elif event.staff3 == None and event.staff3 != username: 
        event.staff3 = username
    
    else:
        print("What the fuck")

    db.session.commit()
    print('hell0')
    e3 = Events.query.filter_by(staff = username).all()
    e2 = Events.query.filter_by(staff2 = username).all()
    e1 = Events.query.filter_by(staff3 = username).all()
    
    query = e1 + e2 + e3

    not_full = Events.query.all()

    for values in query: 
        if values in not_full:
            not_full.remove(values)

    for events in not_full: 
        if events.staff != None and events.staff2 != None and events.staff3 != None: 
            not_full.remove(events)

    return render_template(
        'login.html',
        username = username,
        query = query,
        not_full = not_full,
        permissions='staff'
        )
    
@app.cli.command('initdb')
def initdb_command():
    db.drop_all
    db.create_all()

    m = hashlib.md5(owner_password.encode('utf-8')).hexdigest()
    crypt_pass = str(m)

    owner = User(
        id=str(crypt_pass),
        user=owner_username,
        password=owner_password,
        permissions='owner')

    db.session.add(owner)
    db.session.commit()

def make_date(string):
    the_year = string[:4]
    the_month = string[5:7]
    the_day = string[8:10]
    
    return datetime(
            year = int(the_year),
            month = int(the_month),
            day = int(the_day)
        )

if __name__ == '__main__':
    app.run()
