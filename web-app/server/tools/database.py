import sqlite3
import base64
import time
import random
import string
import bcrypt

def generate_timestamped_string(length=16):
    timestamp = int(time.time())
    base36_timestamp = base36_encode(timestamp)
    random_length = max(0, length - len(base36_timestamp))
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=random_length))
    return base36_timestamp + random_part


def base36_encode(number):
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    return base36


def checkUserExists(username,email):
    db = sqlite3.connect('data.db')
    cursor = db.cursor()
    
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    username_exists = cursor.fetchone() is not None

    cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    email_exists = cursor.fetchone() is not None
    
    db.close()
    return username_exists or email_exists

def createUser(form):
    db = sqlite3.connect('data.db')
    cursor = db.cursor()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(form['password'].encode('utf-8'), salt)
    cursor.execute('''
        INSERT INTO users (id, firstname, lastname, username, email, password)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (generate_timestamped_string(64), form['firstname'], form['lastname'],form['username'],form['email'],hashed_password.decode('utf-8')))

    db.commit()
    db.close()