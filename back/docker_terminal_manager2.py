import os
import select
import fcntl
import threading
import time
import docker
import uuid

class DockerTerminalManager:
    def __init__(self):
        # 도커 클라이언트 초기화
        self.client = docker.from_env()
        
        # 컨테이너 객체 저장 변수
        self.container = None
        
        # 소켓 객체와 파일 디스크립터
        self.socket = None
        self.fd = None
        
        # 터미널 모니터링 스레드 관련 변수를 초기화합니다.
        self.terminal_thread = None
        self.terminal_running = False
        
        # 출력을 처리할 콜백 함수를 저장할 변수입니다.
        self.callback = None
    
    def start_terminal(self, output_callback, image="ubuntu:22.04", command="bash"):
        """새로운 Docker 컨테이너와 터미널 세션을 시작합니다."""
        # 출력을 처리할 콜백 함수를 저장합니다.
        self.callback = output_callback
        
        try:
            # 새 컨테이너 생성 및 실행
            self.container = self.client.containers.run(
                image=image,
                command=command,
                stdin_open=True,
                tty=True,
                environment={"LANG": "KR.UTF-8", "TERM": "xterm-256color"},
                detach=True,
                remove=True  # 컨테이너가 종료되면 자동으로 제거됩니다
            )
            
            # 컨테이너에 연결하기 위한 소켓 생성
            self.socket = self.client.api.attach_socket(
                container=self.container.id,
                params={
                    'stdin': 1,
                    'stdout': 1,
                    'stderr': 1,
                    'stream': 1
                }
            )
            
            # 소켓의 파일 디스크립터 가져오기
            if hasattr(self.socket, 'fileno'):
                self.fd = self.socket.fileno()
            
            # 비동기 I/O를 위해 파일 디스크립터를 비차단 모드로 설정합니다.
            fcntl.fcntl(self.fd, fcntl.F_SETFL, os.O_NONBLOCK)
            
            # 터미널 출력을 모니터링할 백그라운드 스레드를 시작합니다.
            self.terminal_running = True
            self.terminal_thread = threading.Thread(target=self.monitor_output)
            self.terminal_thread.daemon = True  # 메인 프로그램 종료 시 함께 종료되도록 설정
            self.terminal_thread.start()
            
            return self.container.id
        except Exception as e:
            print(f"컨테이너 시작 오류: {str(e)}")
            self.stop_terminal()
            return None
    
    def monitor_output(self):
        """터미널 출력을 백그라운드에서 모니터링합니다."""
        while self.terminal_running and self.fd:
            try:
                # 출력이 있는지 확인합니다.
                r, w, e = select.select([self.fd], [], [], 0.1)
                if r:
                    try:
                        # 컨테이너 출력 데이터를 읽어옵니다.
                        chunk = os.read(self.fd, 4096).decode(errors='replace')
                        if chunk and self.callback:
                            # 데이터가 있을 경우 콜백 함수로 전달합니다.
                            self.callback(chunk)
                    except (OSError, IOError) as e:
                        print(f"터미널 읽기 오류: {str(e)}")
                        break
                time.sleep(0.01)  # CPU 사용량을 줄이기 위한 짧은 지연
            except Exception as e:
                print(f"모니터링 오류: {str(e)}")
                break
        
        print("백그라운드 터미널 모니터링 종료됨")
    
    def send_command(self, command):
        """터미널에 명령어를 전송합니다."""
        if self.socket:
            try:
                print(f"명령어 전송: {command}")
                # 입력된 명령어를 컨테이너에 전송합니다.
                if hasattr(self.socket, 'send'):
                    self.socket.send(command.encode())
                else:
                    os.write(self.fd, command.encode())
                return True
            except Exception as e:
                print(f"명령어 전송 오류: {str(e)}")
                return False
        return False
    
    def resize_terminal(self, rows, cols):
        """터미널 창 크기를 조정합니다."""
        if self.container:
            try:
                # Docker API를 통해 컨테이너 터미널 크기 조정
                self.client.api.resize(self.container.id, height=rows, width=cols)
                print(f"터미널 크기 조정됨: {rows}x{cols}")
                return True
            except Exception as e:
                print(f"터미널 크기 조정 오류: {str(e)}")
                return False
        return False
    
    def stop_terminal(self):
        """터미널 세션과 컨테이너를 종료합니다."""
        self.terminal_running = False  # 모니터링 스레드를 중지합니다.
        
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(f"소켓 종료 오류: {str(e)}")
            self.socket = None
            self.fd = None
        
        if self.container:
            try:
                container_id = self.container.id
                # 컨테이너 정지
                self.container.stop(timeout=1)
                print(f"컨테이너 종료됨, ID: {container_id}")
            except Exception as e:
                print(f"컨테이너 종료 오류: {str(e)}")
            self.container = None


class DockerTerminalSessionManager:
    """여러 세션의 Docker 터미널을 관리하는 클래스"""
    
    def __init__(self):
        # 세션 ID를 키로, DockerTerminalManager 인스턴스를 값으로 갖는 딕셔너리
        self.sessions = {}
    
    def create_session(self, output_callback, image="ubuntu:22.04", command="bash"):
        """새로운 터미널 세션을 생성합니다."""
        # 고유한 세션 ID를 생성합니다
        session_id = str(uuid.uuid4())
        
        # 새 DockerTerminalManager 인스턴스를 생성합니다
        terminal_manager = DockerTerminalManager()
        container_id = terminal_manager.start_terminal(output_callback, image, command)
        
        if container_id:
            # 세션을 저장합니다
            self.sessions[session_id] = terminal_manager
            print(f"새 세션 생성됨: {session_id}, 컨테이너: {container_id}")
            return session_id
        else:
            print("세션 생성 실패")
            return None
    
    def get_session(self, session_id):
        """세션 ID로 DockerTerminalManager 인스턴스를 조회합니다."""
        return self.sessions.get(session_id)
    
    def send_command(self, session_id, command):
        """특정 세션에 명령어를 전송합니다."""
        terminal_manager = self.get_session(session_id)
        if terminal_manager:
            return terminal_manager.send_command(command)
        print(f"세션을 찾을 수 없음: {session_id}")
        return False
    
    def resize_terminal(self, session_id, rows, cols):
        """특정 세션의 터미널 크기를 조정합니다."""
        terminal_manager = self.get_session(session_id)
        if terminal_manager:
            return terminal_manager.resize_terminal(rows, cols)
        print(f"세션을 찾을 수 없음: {session_id}")
        return False
    
    def close_session(self, session_id):
        """세션을 종료하고 리소스를 정리합니다."""
        terminal_manager = self.get_session(session_id)
        if terminal_manager:
            terminal_manager.stop_terminal()
            del self.sessions[session_id]
            print(f"세션 종료됨: {session_id}")
            return True
        print(f"세션을 찾을 수 없음: {session_id}")
        return False
    
    def get_active_sessions(self):
        """활성화된 세션 목록을 반환합니다."""
        return list(self.sessions.keys())


# 애플리케이션 전체에서 사용할 세션 매니저 인스턴스를 생성합니다.
docker_terminal_session_manager = DockerTerminalSessionManager()