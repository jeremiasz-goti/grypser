from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

# -- FORMS --
class GrypsAdd(FlaskForm):
    gryps = StringField('Gryps', validators=[DataRequired(), Length(min=2, max=300)])
    submit = SubmitField('Nadaj Grypsa')

class GrypsDestroy(FlaskForm):
    submit = SubmitField('Spal Grypsa')