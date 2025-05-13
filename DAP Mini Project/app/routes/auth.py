from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models.user import User
from app.utils.forms import RegistrationForm, LoginForm, UpdateAccountForm
import os
from PIL import Image

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Route for user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.welcome'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Route for user login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.welcome'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            # Check for a next parameter, which indicates they were trying to access a protected page
            next_page = request.args.get('next')
            # If there's no next page (meaning they logged in directly), go to welcome page
            if not next_page or not next_page.startswith('/'):
                return redirect(url_for('main.welcome'))
            # Otherwise, redirect to the page they were trying to access
            return redirect(next_page)
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@auth.route('/logout')
def logout():
    """Route for user logout"""
    logout_user()
    return redirect(url_for('main.welcome'))

@auth.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """Route for user account management"""
    form = UpdateAccountForm(current_user.username, current_user.email)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        # Handle profile picture update
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data)
            current_user.image_file = picture_file
        
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('auth.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    image_file = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html', title='Account', image_file=image_file, form=form)

def save_picture(form_picture):
    """Utility function to save profile picture with resizing"""
    from flask import current_app
    import secrets
    
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    # Resize image to save space
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn 