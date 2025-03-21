# Flask 터미널 프로젝트

## 개요
Flask 터미널 프로젝트는 웹 브라우저 내에서 터미널 인터페이스를 제공하는 웹 애플리케이션입니다. 사용자는 실시간으로 명령어를 실행하고 셸 환경과 상호작용할 수 있습니다.

## 할일 목록
- [ ] 유저 관리
   - [ ] 로그인 (명지대 학생인지 질의)
   - [ ] jwt?
   - [ ] 
   - [ ] 
- [ ] 컨테이너 관리
## 설치 방법
1. 저장소를 클론합니다:
   ```
   git clone <repository-url>
   cd {project}
   ```

2. 가상 환경을 생성합니다:
   ```
   python -m venv .venv
   source .venv/bin/activate  # Windows에서는 `.venv\Scripts\activate` 사용
   ```

3. 필요한 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```


## 애플리케이션 실행
애플리케이션을 실행하려면 다음 명령어를 사용합니다:
```
python run.py
```
애플리케이션은 `http://localhost:5000`에서 접속할 수 있습니다.

## 서버 프론트 분리
현재 매우 단순한 ssr 로 되어있습니다

## 테스트
테스트를 실행하려면 다음 명령어를 사용합니다:
```
pytest
```

## 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.