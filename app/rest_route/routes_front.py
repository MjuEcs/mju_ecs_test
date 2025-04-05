from flask import Blueprint, render_template, redirect

front = Blueprint('front', __name__)

@front.route('/')
def index():
    # 클라이언트를 '/home'으로 리다이렉트
    return redirect('/static/index.html')