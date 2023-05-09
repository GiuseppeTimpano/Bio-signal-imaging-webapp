from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_webapp.models import Patient

class LoginForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remeber me')
    submit = SubmitField('Login')

class SignUpForm(FlaskForm):
    first_name = StringField('Name', 
                       validators=[DataRequired()])
    surname = StringField('Surname', 
                          validators=[DataRequired()])
    city = StringField('City', 
                       validators=[DataRequired()])
    CF = StringField('CF', 
                     validators=[DataRequired()])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    confirm_email = StringField('Confirm Email', 
                                validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired()])
    submit = SubmitField('Login')

    def validate_account(self, email):
        email = Patient.query.filter_by(email=self.email.data).first()
        if email:
            raise ValidationError("Already exist an account with this email, please login or create an account with an other email address")
    
    
