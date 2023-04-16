from flask import Flask
from flask import render_template, url_for, flash, redirect

app = Flask(__name__, template_folder='templates_prova')


@app.route("/")
@app.route("/index")
def home():
    return render_template('index.html', title='Start page')

@app.route("/login.html")
def login():
    return render_template('login.html', title='Login')

@app.route("/signup.html")
def signup():
    return render_template('signup.html', title='Sign_up')

if __name__ == '__main__':
    app.run(debug=True)
