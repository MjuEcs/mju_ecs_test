from flask_socketio import emit
from app import socketio
from app.terminal import terminal

@socketio.on('connect')
def handle_connect():
    """클라이언트 연결을 처리합니다."""
    # 터미널 세션을 시작하고 출력을 클라이언트로 전송하는 콜백 함수를 설정합니다.
    def send_output(output):
        socketio.emit('terminal_output', {'output': output})  # 클라이언트에게 터미널 출력을 전송
    
    pid = terminal.start_terminal(send_output)  # 터미널 세션 시작
    print(f"클라이언트가 연결되었습니다. PID: {pid}로 터미널이 시작됨")

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제를 처리합니다."""
    terminal.stop_terminal()  # 터미널 세션 종료
    print("클라이언트 연결이 해제되었습니다. 터미널이 종료됨")

@socketio.on('execute_command')
def handle_command(data):
    """클라이언트로부터 명령어 실행 요청을 처리합니다."""
    terminal.send_command(data['command'])  # 터미널에 명령어 전송

@socketio.on('resize_screen')
def handle_resize(data):
    """클라이언트로부터 터미널 크기 조정 요청을 처리합니다."""
    terminal.resize_terminal(data['rows'], data['cols'])  # 터미널 크기 조정