# Live demo
Check https://grypser.herokuapp.com/ for full experience

# Grypser
An app for sending private and encrypted messages that are deleted after 24 hours or on a button click. Build with Flask and Bootstrap.

# About
The app sends encrypted messages from user to database. The message is accessible after providing valid url address, generated on the fly. Only the receiver of the url adress can read the message and delete it on spot.

If the message is not deleted by the user, the app has a task runner on the database that deletes messages older than 24 hours automatically.

# Ussage 
Share torrent files, streams or links that facebook think are mallicious :P

# To test localy:
Download repo and unpack. Create virtual env and activate it.
Instal requirments with pip install -r requirements.txt
In active virtual env run python3 run.py


