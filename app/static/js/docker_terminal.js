document.addEventListener('DOMContentLoaded', function() {
    // DOM이 완전히 로드되었을 때 실행되는 이벤트 리스너입니다.
    
    // xterm.js 초기화
    Terminal.applyAddon(fit);  // fit 애드온을 적용하여 터미널 크기를 조정할 수 있도록 설정합니다.
    const term = new Terminal({
        cursorBlink: true,  // 커서 깜빡임 효과를 활성화합니다.
        theme: {
            background: '#1e1e1e',  // 배경색을 검정색으로 설정합니다.
            foreground: '#fff'   // 글자색을 흰색으로 설정합니다.
        }
    });
    
    // HTML 문서 내의 'terminal-container' 요소에 터미널을 생성하고 표시합니다.
    term.open(document.getElementById('terminal-container'));
    term.fit();  // 터미널 크기를 컨테이너에 맞게 조정합니다.
    
    // Socket.IO 서버와 연결합니다.
    const socket = io("/docker");
    
    // 서버 연결 이벤트 처리
    socket.on('connect', function() {
        console.log('서버와 연결되었습니다');  // 콘솔에 연결 메시지를 출력합니다.
        term.writeln('서버와 연결되었습니다');  // 터미널에 연결 메시지를 표시합니다.
        
        // 현재 터미널 크기를 서버로 전송합니다.
        updateTerminalSize();
    });
    
    // 서버 연결 해제 이벤트 처리
    socket.on('disconnect', function() {
        console.log('서버와 연결이 끊어졌습니다');  // 콘솔에 연결 해제 메시지를 출력합니다.
        term.writeln('\r\n서버와 연결이 끊어졌습니다');  // 터미널에 연결 해제 메시지를 표시합니다.
    });
    
    // 서버로부터 받은 터미널 출력을 처리합니다.
    socket.on('terminal_output', function(data) {
        term.write(data.output);  // 터미널에 서버로부터 받은 출력 데이터를 표시합니다.
    });
    
    // 사용자가 입력한 데이터를 서버로 전송합니다.
    term.on('data', function(data) {
        socket.emit('execute_command', { command: data });  // 사용자 입력을 서버로 전달합니다.
    });
    
    // 터미널 크기 업데이트 함수
    function updateTerminalSize() {
        const dims = {
            cols: term.cols,  // 현재 터미널의 열 개수
            rows: term.rows   // 현재 터미널의 행 개수
        };
        socket.emit('resize_screen', dims);  // 새로운 크기를 서버로 전송합니다.
    }
    
    // 윈도우 크기 변경 이벤트를 감지하여 터미널 크기를 조정합니다.
    window.addEventListener('resize', function() {
        term.fit();  // 터미널 크기를 다시 조정합니다.
        updateTerminalSize();  // 새로운 크기를 서버로 전송합니다.
    });
});