from flask import Flask
from flask import render_template, url_for, flash, redirect
from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f0d9750d6c694693beba7b033d08a66b'


@app.route("/")
@app.route("/index")
def home():
    return render_template('index.html', title='Start page')

@app.route("/login.html", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data=='prova@unicz.it' and form.password=='prova':
            flash('You have been logged in!')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/signup.html")
def signup():
    return render_template('signup.html', title='Sign_up')


if __name__ == '__main__':
    app.run(debug=True)
