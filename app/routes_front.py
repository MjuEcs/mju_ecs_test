from flask import Blueprint, render_template

front = Blueprint('front', __name__)

@front.route('/')
def index():
    """Render welcome patge"""
    return render_template('index.html')

@front.route('/terminal')
def terminal():
    """Render the terminal page"""
    return render_template('terminal.html')