import os
import pty
import select
import termios
import struct
import fcntl
import signal
import threading
import time

class OsTerminal:
    def __init__(self):
        # 파일 디스크립터와 자식 프로세스 ID를 초기화합니다.
        self.fd = None
        self.child_pid = None
        
        # 터미널 모니터링 스레드 관련 변수를 초기화합니다.
        self.terminal_thread = None
        self.terminal_running = False
        
        # 출력을 처리할 콜백 함수를 저장할 변수입니다.
        self.callback = None
    
    def start_terminal(self, output_callback):
        """새로운 터미널 세션을 시작합니다."""
        # 출력을 처리할 콜백 함수를 저장합니다.
        self.callback = output_callback
        
        # 새로운 가상 터미널(PTY)을 생성하고 자식 프로세스를 포크합니다.
        (self.child_pid, self.fd) = pty.fork()
        
        if self.child_pid == 0:
            # 자식 프로세스에서는 쉘(/bin/bash)을 실행합니다.
            env = os.environ.copy()  # 현재 환경 변수를 복사합니다.
            env["TERM"] = "xterm-256color"  # 터미널 타입을 설정합니다.
            os.execvpe('/bin/bash', ['/bin/bash'], env)  # bash 실행
            
        else:
            # 부모 프로세스에서는 비동기 I/O를 위해 파일 디스크립터를 비차단 모드로 설정합니다.
            fcntl.fcntl(self.fd, fcntl.F_SETFL, os.O_NONBLOCK)
            
            # 터미널 출력을 모니터링할 백그라운드 스레드를 시작합니다.
            self.terminal_running = True
            self.terminal_thread = threading.Thread(target=self.monitor_output)
            self.terminal_thread.daemon = True  # 메인 프로그램 종료 시 함께 종료되도록 설정
            self.terminal_thread.start()
            
            return self.child_pid  # 자식 프로세스의 PID를 반환합니다.
    
    def monitor_output(self):
        """터미널 출력을 백그라운드에서 모니터링합니다."""
        while self.terminal_running and self.fd:
            # 출력이 있는지 확인합니다.
            r, w, e = select.select([self.fd], [], [], 0.1)  # 읽기 가능한지 확인
            if r:
                try:
                    # 터미널에서 데이터를 읽어옵니다.
                    chunk = os.read(self.fd, 1024).decode(errors='replace')
                    if chunk and self.callback:
                        # 데이터가 있을 경우 콜백 함수로 전달합니다.
                        self.callback(chunk)
                except (OSError, IOError) as e:
                    print(f"터미널 읽기 오류: {str(e)}")
                    break
            time.sleep(0.05)  # CPU 사용량을 줄이기 위한 짧은 지연
        
        print("백그라운드 터미널 모니터링 종료됨")
    
    def send_command(self, command):
        """터미널에 명령어를 전송합니다."""
        if self.fd:
            print(f"명령어 전송: {command}")
            print(f"바이트 {command.encode()}")
            # 입력된 명령어를 터미널에 전송합니다.
            os.write(self.fd, command.encode())
    
    def resize_terminal(self, rows, cols):
        """터미널 창 크기를 조정합니다."""
        if self.fd:
            try:
                # winsize 구조체를 생성하여 행과 열 정보를 설정합니다.
                winsize = struct.pack("HHHH", rows, cols, 0, 0)
                fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)  # 크기 변경 요청
                print(f"터미널 크기 조정됨: {rows}x{cols}")
            except Exception as e:
                print(f"터미널 크기 조정 오류: {str(e)}")
    
    def stop_terminal(self):
        """터미널 세션을 종료합니다."""
        self.terminal_running = False  # 모니터링 스레드를 중지합니다.
        
        if self.child_pid:
            try:
                # 자식 프로세스를 강제 종료합니다.
                os.kill(self.child_pid, signal.SIGTERM)
            except OSError:
                pass
            print(f"터미널 종료됨, PID: {self.child_pid}")
            
            # 리소스를 정리합니다.
            self.child_pid = None
            self.fd = None

# 애플리케이션 전체에서 사용할 싱글톤 인스턴스를 생성합니다.
os_terminal = OsTerminal()