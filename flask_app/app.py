from flask import Flask
from flask import render_template, url_for, flash, redirect
from flask import session
from flask_login import logout_user
from forms import LoginForm, SignUpForm

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
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            session['name'] = "admin"
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            #return redirect(url_for('login'))
    return render_template('login.html', title='Login', form=form, name=session.get('name'))

@app.route("/signup.html", methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if form.first_name.data == 'Giuseppe' and form.surname.data == 'Timpano':
            flash('You have been signup!', 'success')
    return render_template('signup.html', title='Sign_up', form=form)

@app.route("/sign_out")
def logout():
    session.pop('name')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
