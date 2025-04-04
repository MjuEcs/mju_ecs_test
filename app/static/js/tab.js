document.addEventListener('DOMContentLoaded', function () {
    const { Terminal } = window.Terminal;
    const { FitAddon } = window.FitAddon;

    // 상태 관리
    let terminalCount = 1; // 현재 터미널 개수
    const terminals = {};   // 각 터미널 인스턴스 저장

    // DOM 요소 참조
    const tabsContainer = document.getElementById('terminal-tabs');
    const contentContainer = document.getElementById('terminal-content');
    const addTerminalButton = document.getElementById('add-terminal');

    // 새로운 터미널 생성 함수
    function createTerminal() {
        const tabId = `terminal-${terminalCount}`;
        const isActive = terminalCount === 1; // 첫 번째 탭만 활성화

        // 탭 메뉴 추가
        const tabButton = document.createElement('button');
        tabButton.className = `nav-link ${isActive ? 'active' : ''}`;
        tabButton.setAttribute('data-bs-toggle', 'tab');
        tabButton.setAttribute('data-tab-id', terminalCount);
        tabButton.textContent = `Terminal ${terminalCount}`;
        tabsContainer.appendChild(tabButton);

        // 탭 컨텐츠 추가
        const tabContent = document.createElement('div');
        tabContent.className = `tab-pane fade ${isActive ? 'show active' : ''}`;
        tabContent.id = tabId;
        contentContainer.appendChild(tabContent);

        // xterm.js 초기화
        const fitAddon = new FitAddon();
        const term = new Terminal({
            cursorBlink: true,
            theme: {
                background: '#000',
                foreground: '#fff'
            }
        });
        term.loadAddon(fitAddon);
        term.open(tabContent);
        fitAddon.fit();

        // Socket.IO 연결
        const socket = io('/docker');
        socket.on('connect', () => {
            console.log(`Socket connected for Terminal ${terminalCount}`);
            term.writeln('서버와 연결되었습니다');
            updateTerminalSize(term, socket);
        });

        socket.on('disconnect', () => {
            term.writeln('\r\n서버와 연결이 끊어졌습니다');
        });

        socket.on('terminal_output', (data) => {
            term.write(data.output);
        });

        term.on('data', (data) => {
            socket.emit('execute_command', { command: data });
        });

        // 상태 저장
        terminals[terminalCount] = { term, socket, fitAddon };

        // 윈도우 크기 변경 이벤트 처리
        window.addEventListener('resize', () => {
            if (tabButton.classList.contains('active')) {
                fitAddon.fit();
                updateTerminalSize(term, socket);
            }
        });

        terminalCount++;
    }

    // 터미널 크기 업데이트 함수
    function updateTerminalSize(term, socket) {
        const dims = {
            cols: term.cols,
            rows: term.rows
        };
        socket.emit('resize_screen', dims);
    }

    // 탭 전환 이벤트 처리
    tabsContainer.addEventListener('click', (e) => {
        const tabButton = e.target.closest('.nav-link');
        if (!tabButton) return;

        const tabId = tabButton.getAttribute('data-tab-id');
        const terminal = terminals[tabId];

        if (terminal) {
            terminal.fitAddon.fit();
            updateTerminalSize(terminal.term, terminal.socket);
        }
    });

    // 새로운 터미널 추가 버튼 클릭 이벤트
    addTerminalButton.addEventListener('click', () => {
        createTerminal();
    });

    // 초기 터미널 생성
    createTerminal();
});