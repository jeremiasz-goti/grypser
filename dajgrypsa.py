from flask import Flask, render_template, url_for, redirect
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
    gryps_id = db.Column(db.String(10), unique=True)
    gryps_content = db.Column(db.String(300), unique=False, nullable=True)

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
    if form.validate_on_submit():
        gryps_id = ''.join(secrets.choice(alphabet) for i in range(10))
        gryps = Gryps(gryps_id=gryps_id, gryps_content=form.gryps.data)
        db.session.add(gryps)
        db.session.commit()
        return redirect(url_for('gryps', gryps_id=gryps_id))
    return render_template('home.html', form=form)


@app.route('/gryps/<gryps_id>', methods=['GET', 'POST'])
def gryps(gryps_id):
    gryps = Gryps.query.filter_by(gryps_id=gryps_id).first_or_404()
    return render_template('gryps.html', gryps=gryps, title='Gryps')



if __name__ == '__main__':
    app.run(debug=True)