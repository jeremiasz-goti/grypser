from flask import Flask, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import secrets
import string


# --- APP CONFIG
app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grypsy.db'

# --- CRYPTOGRAPHY
""" TO DO: If file key.key doesn`t exist, create one, and if it already exists, read the key from that file"""
# key = Fernet.generate_key()
# file = open('key.key', 'wb')
# file.write(key)
# file.close()

""" Reads key for decryption """
file = open('key.key', 'rb')  # open file
hash_key = file.read()  # read file
file.close()  # close file
f = Fernet(hash_key) # hashing key


# --- TASK RUNNER
""" Runs operations on the database in the background. Might do cron-jobs later """
def check_database():
    print("Checking database " + str(datetime.utcnow()))
    gryps_check = Gryps.query.order_by(Gryps.gryps_creation) # get messages sorted by creation date
    for g in gryps_check: # loop for going through rows
        if g.gryps_destroy <= datetime.utcnow(): # if message destroy time is older than the check - delete message
            print( str(g.gryps_id) + " Ready for termination")
            db.session.delete(g)
            db.session.commit()
        else:
            print("Nothing in database or something is still alive")

""" Run tasker """
tasker = BackgroundScheduler(daemon=True)
tasker.add_job(check_database,'interval',minutes=1)
tasker.start()

# --- DATABASE MODELS
class Gryps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gryps_id = db.Column(db.String(10), unique=True)
    gryps_content = db.Column(db.String(300), unique=False, nullable=True)
    gryps_creation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    gryps_destroy = db.Column(db.DateTime, nullable=False, default=(datetime.utcnow() + timedelta(hours=24)))

    def __repr__(self):
        return f"Gryps('{self.id}', '{self.gryps_id}', '{self.gryps_content}, '{self.gryps_creation}', '{self.gryps_destroy}')"

# -- FORMS --
class GrypsAdd(FlaskForm):
    gryps = StringField('Gryps', validators=[DataRequired(), Length(min=2, max=300)])
    submit = SubmitField('Nadaj Grypsa')

class GrypsDestroy(FlaskForm):
    submit = SubmitField('Spal Grypsa')


# --- ROUTINGS ---
@app.route('/', methods=['GET', 'POST'])
def home():
    form = GrypsAdd()
    if form.validate_on_submit():

        """ Generate uniqe url for messages - imports alphabet and digits an generates random 10-digit url from letters and numbers """
        alphabet = string.ascii_letters + string.digits # join letters and digits
        gryps_id = ''.join(secrets.choice(alphabet) for i in range(10)) # render unique url

        """ Encoding message and sending it to database"""
        gryps_form_text = (form.gryps.data) # get text from form
        gryps_encrypt = f.encrypt(gryps_form_text.encode()) # encrypt the text from form

        """ Database entry """
        gryps = Gryps(gryps_id=gryps_id, gryps_content=gryps_encrypt) # create db entry
        db.session.add(gryps) # add
        db.session.commit() # commit to database
        return redirect(url_for('gryps', gryps_id=gryps_id)) # redirect to message page
    return render_template('home.html', form=form) # render home template with form


@app.route('/gryps/<gryps_id>', methods=['GET', 'POST']) # message page with dynamic url
def gryps(gryps_id): # passing variables

    form = GrypsDestroy() # generate form to destroy messsage
    gryps = Gryps.query.filter_by(gryps_id=gryps_id).first_or_404() # get message from db

    """ Reads key for decryption """
    file = open('key.key', 'rb') # open file
    dehash_key = file.read() # read file
    file.close() # close file

    """ Decoding messages """
    f2 = Fernet(dehash_key) # imported key for decrypting
    gryps_hashed = gryps.gryps_content # get hashed message content from db
    gryps_unhashed = f2.decrypt(gryps_hashed) # decrypt message with key
    gryps_decode = gryps_unhashed.decode()  # decode message

    """ Delete message """
    if form.validate_on_submit():
        db.session.delete(gryps) # set message to be deleted
        db.session.commit() # delete message
        return redirect(url_for('home')) # redirect to homepage
    return render_template('gryps.html', gryps_decode=gryps_decode, gryps=gryps, form=form, title='Gryps') # render basic massage template



if __name__ == '__main__':
    app.run(debug=True)