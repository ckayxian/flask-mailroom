import os

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import Donation, Donor, User 

app = Flask(__name__)

default_key = b'\x8b\x95\x89\x03\x14Cq2\xa8T\xb2\x8d\xf8\xbc\xaf\xb9\x12\xcaS=\xb7\x99\xe6\xef'
app.secret_key = os.environ.get('SECRET_KEY', default_key)

@app.route('/')
def home():
    return redirect(url_for('all'))

@app.route('/donations/')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)

@app.route('/create', methods=['GET', 'POST'])
def create():
    # require that users login in order to enter a donation
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            donor = Donor.select().where(Donor.name == request.form['name']).get()
            if donor:
                donoation = Donation(value=request.form['value'], donor=donor)
                donoation.save()
                return redirect(url_for('all'))
        except Donor.DoesNotExist:
            # re-display the donation creation form and inject a message describing the error
            return render_template('create.jinja2', error="Donor does not exist")
    else:
        return render_template('create.jinja2')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = User.select().where(User.username == request.form['username']).get()
            if user and pbkdf2_sha256.verify(request.form['password'], user.password):
                session['username'] = request.form['username']
                return redirect(url_for('create'))
        except User.DoesNotExist:
            return render_template('login.jinja2', error="Incorrect username or password")
    else:
        return render_template('login.jinja2')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

