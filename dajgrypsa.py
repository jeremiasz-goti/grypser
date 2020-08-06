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
key = Fernet.generate_key()
f = Fernet(key)
file = open('key.key', 'wb')
file.write(key)
file.close()

# --- TASK RUNNER
def check_database():
    print("Checking database " + str(datetime.utcnow()))

tasker = BackgroundScheduler(daemon=True)
tasker.add_job(check_database,'interval',minutes=5)
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
        alphabet = string.ascii_letters + string.digits
        gryps_id = ''.join(secrets.choice(alphabet) for i in range(10))

        """ Encoding message and sending it to database"""
        gryps_form_text = (form.gryps.data) # get text from form
        gryps_encrypt = f.encrypt(gryps_form_text.encode()) # encrypt the text from form

        """ Database entry """
        gryps = Gryps(gryps_id=gryps_id, gryps_content=gryps_encrypt) # create db entry
        db.session.add(gryps) # add
        db.session.commit() # commit to database
        return redirect(url_for('gryps', gryps_id=gryps_id)) #redirect to message page
    return render_template('home.html', form=form)


@app.route('/gryps/<gryps_id>', methods=['GET', 'POST'])
def gryps(gryps_id):

    form = GrypsDestroy()
    gryps = Gryps.query.filter_by(gryps_id=gryps_id).first_or_404()

    """ Reads key for decryption """
    file = open('key.key', 'rb') # open file
    dehash_key = file.read() # read file
    file.close() # close file

    """ Decoding messages """
    f2 = Fernet(dehash_key) # imported key for decrypting
    gryps_hashed = gryps.gryps_content
    gryps_unhashed = f2.decrypt(gryps_hashed)
    gryps_decode = gryps_unhashed.decode()

    """ Delete message """
    if form.validate_on_submit():
        db.session.delete(gryps)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('gryps.html', gryps_decode=gryps_decode, gryps=gryps, form=form, title='Gryps')



if __name__ == '__main__':
    app.run(debug=True)