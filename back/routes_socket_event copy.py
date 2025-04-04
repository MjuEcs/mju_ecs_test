from flask_socketio import emit, request
from app import socketio
from app.os_terminal_manager import terminal
from app.docker_terminal_manager import docker_terminal
from app.docker_terminal_registry import terminal_registry

### 운영체제 터미널 관련 socketio 이벤트 핸들러
@socketio.on('connect', namespace='/os')
def handle_connect():
    """클라이언트 연결을 처리합니다."""
    # 터미널 세션을 시작하고 출력을 클라이언트로 전송하는 콜백 함수를 설정합니다.
    def send_output(output):
        socketio.emit('terminal_output', {'output': output}, namespace='/os')  # 클라이언트에게 터미널 출력을 전송
    
    pid = terminal.start_terminal(send_output)  # 터미널 세션 시작
    print(f"클라이언트가 연결되었습니다. PID: {pid}로 터미널이 시작됨")

@socketio.on('disconnect', namespace='/os')
def handle_disconnect():
    """클라이언트 연결 해제를 처리합니다."""
    terminal.stop_terminal()  # 터미널 세션 종료
    print("클라이언트 연결이 해제되었습니다. 터미널이 종료됨")

@socketio.on('execute_command', namespace='/os')
def handle_command(data):
    """클라이언트로부터 명령어 실행 요청을 처리합니다."""
    terminal.send_command(data['command'])  # 터미널에 명령어 전송

@socketio.on('resize_screen', namespace='/os')
def handle_resize(data):
    """클라이언트로부터 터미널 크기 조정 요청을 처리합니다."""
    terminal.resize_terminal(data['rows'], data['cols'])  # 터미널 크기 조정

##########################################################################
###               docker terminal 관련 socketio 이벤트 핸들러           ###
##########################################################################

@socketio.on('connect', namespace='/docker')
def handle_connect():
    """클라이언트 연결을 처리합니다."""
    socket_id = request.sid  # 소켓 ID로 사용자 식별
    
    # 터미널 세션을 시작하고 출력을 클라이언트로 전송하는 콜백 함수를 설정합니다.
    def send_output(output):
        socketio.emit('terminal_output', {'output': output}, namespace='/docker', room=socket_id)
    
    # 해당 사용자를 위한 새 터미널 인스턴스 생성
    docker_terminal = terminal_registry.create_terminal(socket_id)
    pid = docker_terminal.start_terminal(send_output)  # 터미널 세션 시작
    print(f"클라이언트({socket_id})가 연결되었습니다. PID: {pid}로 터미널이 시작됨")

@socketio.on('disconnect', namespace='/docker')
def handle_disconnect():
    """클라이언트 연결 해제를 처리합니다."""
    socket_id = request.sid
    terminal_registry.remove_terminal(socket_id)
    print(f"클라이언트({socket_id}) 연결이 해제되었습니다. 터미널이 종료됨")

@socketio.on('execute_command', namespace='/docker')
def handle_command(data):
    """클라이언트로부터 명령어 실행 요청을 처리합니다."""
    socket_id = request.sid
    docker_terminal = terminal_registry.get_terminal(socket_id)
    if docker_terminal:
        docker_terminal.send_command(data['command'])  # 터미널에 명령어 전송

@socketio.on('resize_screen', namespace='/docker')
def handle_resize(data):
    """클라이언트로부터 터미널 크기 조정 요청을 처리합니다."""
    socket_id = request.sid
    docker_terminal = terminal_registry.get_terminal(socket_id)
    if docker_terminal:
        docker_terminal.resize_terminal(data['rows'], data['cols'])  # 터미널 크기 조정
        
@socketio.on('connect_to_container', namespace='/docker')
def handle_container_connect(data):
    """특정 컨테이너에 연결 요청을 처리합니다."""
    socket_id = request.sid
    container_name = data.get('container_name')
    
    # 기존 터미널 종료 후 새로운 컨테이너 연결
    terminal_registry.remove_terminal(socket_id)
    
    # 터미널 출력 콜백 함수
    def send_output(output):
        socketio.emit('terminal_output', {'output': output}, namespace='/docker', room=socket_id)
    
    # 지정된 컨테이너로 새 터미널 생성
    docker_terminal = terminal_registry.create_terminal(socket_id, container_name)
    pid = docker_terminal.start_terminal(send_output)
    
    print(f"클라이언트({socket_id})가 컨테이너 {container_name}에 연결됨. PID: {pid}")
    return {"status": "success", "message": f"Connected to container {container_name}"}