from threading import Lock
from app.docker_terminal_manager import DockerTerminalManager

class DockerTerminalRegistry:
    """사용자별 도커 터미널 인스턴스를 관리하는 레지스트리 클래스"""
    
    def __init__(self):
        self._terminals = {}  # 소켓ID를 키로 하는 터미널 매니저 딕셔너리
        self._lock = Lock()   # 스레드 안전을 위한 락
    
    def create_terminal(self, socket_id, container_name=None):
        """새 터미널 인스턴스 생성"""
        with self._lock:
            # 기존 터미널이 있다면 정리
            if socket_id in self._terminals:
                self._terminals[socket_id].stop_terminal()
            
            # 새 터미널 인스턴스 생성
            terminal = DockerTerminalManager(container_name)
            self._terminals[socket_id] = terminal
            return terminal
    
    def get_terminal(self, socket_id):
        """소켓ID에 해당하는 터미널 반환"""
        with self._lock:
            return self._terminals.get(socket_id)
    
    def remove_terminal(self, socket_id):
        """터미널 인스턴스 제거"""
        with self._lock:
            if socket_id in self._terminals:
                self._terminals[socket_id].stop_terminal()
                del self._terminals[socket_id]
    
    def terminal_exists(self, socket_id):
        """터미널 존재 여부 확인"""
        with self._lock:
            return socket_id in self._terminals

# 전역 레지스트리 인스턴스
terminal_registry = DockerTerminalRegistry()