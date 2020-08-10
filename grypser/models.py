from grypser import db
from datetime import datetime, timedelta

# --- DATABASE MODELS
class Gryps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gryps_id = db.Column(db.String(10), unique=True)
    gryps_content = db.Column(db.String(300), unique=False, nullable=True)
    gryps_creation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    gryps_destroy = db.Column(db.DateTime, nullable=False, default=(datetime.utcnow() + timedelta(hours=24)))

    def __repr__(self):
        return f"Gryps('{self.id}', '{self.gryps_id}', '{self.gryps_content}, '{self.gryps_creation}', '{self.gryps_destroy}')"