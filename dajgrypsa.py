from flask import Flask, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy

import secrets
import string

alphabet = string.ascii_letters + string.digits

# --- APP CONFIG
app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grypsy.db'

# --- DATABASE MODELS
class Gryps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gryps_id = db.Column(db.String(10), default=''.join(secrets.choice(alphabet) for i in range(10)), unique=True)
    gryps_content = db.Column(db.String(300), unique=False, nullable=False)

    def __repr__(self):
        return f"Gryps('{self.id}', '{self.gryps_id}', '{self.gryps_content}')"

# -- FORMS --
class GrypsAdd(FlaskForm):
    gryps = StringField('Gryps', validators=[DataRequired(), Length(min=2, max=300)])
    submit = SubmitField('Nadaj Grypsa')

class GrypsDestroy(FlaskForm):
    destroy = SubmitField('Spal Grypsa')

# --- ROUTINGS ---
@app.route('/', methods=['GET', 'POST'])
def home():
    form = GrypsAdd()
    return render_template('home.html', form=form)

@app.route('/gryps', methods=['GET', 'POST'])
def gryps():
    form = GrypsDestroy()
    return render_template('gryps.html', form=form, title='Gryps')



if __name__ == '__main__':
    app.run(debug=True)