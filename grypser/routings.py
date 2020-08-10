from flask import render_template, url_for, redirect
from grypser import app, db
from grypser.forms import GrypsAdd, GrypsDestroy
from grypser.models import Gryps
import secrets
import string

from cryptography.fernet import Fernet


# --- CRYPTOGRAPHY

""" Reads key for decryption """
try:
    file = open('keyfile.key', 'rb')  # open file
    hash_key = file.read()  # read file
    file.close()  # close file
    f = Fernet(hash_key)  # hashing key
    print("Found key file - Reading")
except FileNotFoundError:
    key = Fernet.generate_key()
    file = open('keyfile.key', 'wb')
    file.write(key)
    file.close()
    print("Creating new key file")


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
