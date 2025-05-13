from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, FloatField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User
from app.models.category import Category
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UpdateAccountForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already registered. Please use a different one.')

class TransactionForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=datetime.utcnow)
    description = StringField('Description', validators=[Length(max=255)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    type = SelectField('Type', choices=[('income', 'Income'), ('expense', 'Expense')], validators=[DataRequired()])
    submit = SubmitField('Add Transaction')
    
    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        # By default, show expense categories (most common case)
        # The route will update these choices when needed
        self.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(type='expense').order_by(Category.name).all()]

class BudgetForm(FlaskForm):
    amount = FloatField('Budget Amount', validators=[DataRequired()])
    year = SelectField('Year', coerce=int, validators=[DataRequired()])
    month = SelectField('Month', coerce=int, choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), 
                                                   (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
                                                   (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], 
                      validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Set Budget')
    
    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(type='expense').order_by(Category.name).all()]
        
        # Set year choices (current year and next 5 years)
        current_year = datetime.utcnow().year
        self.year.choices = [(year, str(year)) for year in range(current_year, current_year + 6)]

class ReportFilterForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    report_type = SelectField('Report Type', choices=[('all', 'All Transactions'), 
                                                  ('income', 'Income Only'), 
                                                  ('expense', 'Expenses Only')], 
                           validators=[DataRequired()])
    format = SelectField('Format', choices=[('pdf', 'PDF'), ('excel', 'Excel')], validators=[DataRequired()])
    submit = SubmitField('Generate Report') 