from flask import Flask
from flask_socketio import SocketIO

# 전역 변수로 SocketIO 객체를 생성합니다.
socketio = SocketIO()

def create_app(config_object=None):
    """
    Flask 애플리케이션을 생성하고 초기화합니다.
    """
    # Flask 애플리케이션을 생성합니다.
    app = Flask(__name__,
                static_url_path='/',  # 정적 파일 경로 설정
                static_folder='static',  # 정적 파일 폴더 지정
                template_folder='templates')  # 템플릿 폴더 지정
    
    # 시크릿 키 설정 (보안 관련, 세션 관리 등에 사용)
    app.config['SECRET_KEY'] = 'secret!'
    
    # 외부 설정 객체가 제공된 경우 이를 로드하여 애플리케이션 설정을 업데이트합니다.
    if config_object:
        app.config.from_object(config_object)
    
    # SocketIO를 Flask 애플리케이션과 연결합니다.
    socketio.init_app(app)
    
    # 블루프린트 등록 (라우팅을 모듈화하여 관리)
    from app.routes_rest import main as main_blueprint
    from app.routes_front import front as front_blueprint
    app.register_blueprint(main_blueprint)  # 메인 라우트를 애플리케이션에 등록
    app.register_blueprint(front_blueprint)
        
    # SocketIO 이벤트 초기화 (소켓 이벤트 핸들러 등록)
    from app import routes_socket_event  # 소켓 이벤트 핸들러를 포함한 모듈을 임포트
    
    return app  # 초기화된 Flask 애플리케이션을 반환