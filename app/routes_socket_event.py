import docker
from flask import request
from flask_socketio import emit
from app import socketio
from app.docker_terminal_manager import DockerTerminalManager
import threading

##########################################################################
###               docker terminal 관련 socketio 이벤트 핸들러           ###
##########################################################################

docker_terminal_managers = {}
docker_terminal_lock = threading.Lock()

@socketio.on('connect', namespace='/docker')
def handle_connect():
    """클라이언트 연결을 처리합니다."""
    sid = request.sid  # Socket.IO 세션 ID
    
    print(f"연결된 터미널 개수: {docker_terminal_managers.__len__()}")
    
    def send_output(output):
        """터미널 출력을 클라이언트에게 전송합니다."""
        socketio.emit('terminal_output', {'output': output}, namespace='/docker', room=sid)
    
    # 새로운 DockerTerminalManager 인스턴스 생성 및 시작
    manager = DockerTerminalManager()
    pid = manager.start_terminal(send_output)
    
    with docker_terminal_lock:
        docker_terminal_managers[sid] = manager  # 세션별로 관리
    
    print(f"클라이언트가 연결되었습니다. SID: {sid}, PID: {pid}로 터미널이 시작됨")

@socketio.on('disconnect', namespace='/docker')
def handle_disconnect():
    """클라이언트 연결 해제를 처리합니다."""
    sid = request.sid  # Socket.IO 세션 ID
    
    with docker_terminal_lock:
        if sid in docker_terminal_managers:
            manager = docker_terminal_managers.pop(sid)  # 세션에서 제거
            manager.stop_terminal()  # 터미널 세션 종료
    
    print(f"클라이언트 연결이 해제되었습니다. SID: {sid}. 터미널이 종료됨")

@socketio.on('execute_command', namespace='/docker')
def handle_command(data):
    """클라이언트로부터 명령어 실행 요청을 처리합니다."""
    sid = request.sid
    with docker_terminal_lock:
        if sid in docker_terminal_managers:
            manager = docker_terminal_managers[sid]
            manager.send_command(data['command'])  # 터미널에 명령어 전송

@socketio.on('resize_screen', namespace='/docker')
def handle_resize(data):
    """클라이언트로부터 터미널 크기 조정 요청을 처리합니다."""
    sid = request.sid
    with docker_terminal_lock:
        if sid in docker_terminal_managers:
            manager = docker_terminal_managers[sid]
            manager.resize_terminal(data['rows'], data['cols'])  # 터미널 크기 조정