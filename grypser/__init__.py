from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


# --- APP CONFIG
app = Flask(__name__)
db = SQLAlchemy(app)
DATABASE_URL = 'sqlite:///grypsy.db'
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

from grypser import routings
from grypser.models import Gryps

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
            print("Database empty.")

def stats():
    print("Stats go in here")

""" Run tasker """
tasker = BackgroundScheduler(daemon=True)
tasker.add_job(check_database,'interval', minutes=1)
tasker.add_job(stats, 'interval', seconds=5)
tasker.start()