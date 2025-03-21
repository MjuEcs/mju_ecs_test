from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.get('/users/<int:user_id>/containers')
def get_containers(user_id):
    """
    사용자의 컨테이너 목록을 반환합니다. json 형식으로 반환합니다.
    """
    
    