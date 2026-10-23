from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/welcome')
def welcome():
    """Render the welcome page with website description"""
    return render_template('welcome.html', title='Welcome')

@main.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html', title='About') 