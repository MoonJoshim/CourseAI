## CourseAI

에브리타임 강의평을 기반으로 강의 검색/요약/추천을 제공하는 풀스택 프로젝트입니다. 셀레니움을 사용해 강의 데이터를 수집하고, Flask API로 가공해 React 프론트엔드에 제공합니다. 벡터 파이프라인(mock)으로 향후 임베딩/검색 확장을 대비했습니다.

### 주요 기능
- **강의 검색(한글 지원)**: 에브리타임 강의실에서 키워드로 강의 검색
- **AI 친화적 응답 구조**: 프론트엔드가 바로 사용하는 통일된 강의 데이터 스키마
- **크롤링 설정/쿠키 로그인**: `.env`와 쿠키 파일 기반의 안정적 로그인 흐름
- **벡터 파이프라인(mock)**: 임베딩 업서트/쿼리 흐름을 로컬에서 시뮬레이션

### 아키텍처
- **backend (Flask + Selenium)**: 에브리타임 로그인/검색 및 API 제공
- **frontend (React 18)**: 강의 검색 UI 및 결과 표시
- **config**: 환경변수 로딩 및 크롤링 파라미터
- **vector_pipeline**: 임베딩 업서트/검색을 흉내내는 로컬 목 스크립트

### 디렉터리 구조
- `backend/`: 크롤러 및 API 서버
  - `final_korean_api.py`: 한글 지원 검색 API 서버(셀레니움 + CORS)
  - `api/lecture_api.py`, `api/ai_api.py`: 통합 API 로직(확장/통합 시 사용)
  - `crawler/evertime_crawler.py`: 크롤러 모듈
  - `everytime_cookies.json`: 로그인 세션 쿠키 파일
- `frontend/react-app/`: React 앱(CRA)
- `config/`
  - `config.py`: 환경설정 로딩
  - `env.example`: 환경변수 템플릿
- `vector_pipeline/`
  - `upsert_mock.py`, `query_mock.py`, `mock_data.jsonl`
- `requirements.txt`: 백엔드 공통 의존성
- `venv/`: 로컬 가상환경(옵션)

### 기술 스택
- **Backend**: Python 3.9+, Flask, Selenium, BeautifulSoup, Requests, Pandas
- **Frontend**: React 18 (CRA), lucide-react
- **Infra/기타**: python-dotenv, Flask-CORS, webdriver-manager

### 사전 준비물
- macOS/Windows/Linux, Python 3.9+, Node.js 18+ 및 npm
- Chrome 설치(셀레니움 크롬드라이버 사용)
- 에브리타임 계정

### 설치
1) 저장소 클론
```bash
git clone <REPO_URL>
cd CourseAI
```

2) 백엔드 의존성
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3) 프론트엔드 의존성
```bash
cd frontend/react-app
npm install
```

### 환경 변수 설정
- `config/env.example`를 참조해 루트 혹은 `backend/` 실행 경로에서 `.env` 파일 생성:
```bash
cp config/env.example .env
```
- 주요 키
  - `EVERYTIME_ID` / `EVERYTIME_PASSWORD`: 에브리타임 로그인 정보
  - `HEADLESS_MODE`: `true|false` (크롬 헤드리스)
  - `DELAY_BETWEEN_REQUESTS`: 요청 간 지연(초)
  - `LOG_LEVEL`: `INFO|DEBUG` 등

환경변수는 `config/config.py`에서 로드/검증됩니다.

### 쿠키 로그인 준비(중요)
- 최초 한 번 수동 로그인으로 `backend/everytime_cookies.json`을 준비해야 합니다.
- `final_korean_api.py`는 해당 쿠키를 로드해 자동 로그인합니다. 쿠키가 만료되면 파일을 갱신하세요.

수동 로그인 스크립트가 없는 경우, 크롬 개발자도구로 로그인 후 쿠키를 추출하여 JSON 배열 형태로 `backend/everytime_cookies.json`에 저장하세요.

### 실행 방법
- 터미널 1: 백엔드(API)
```bash
cd backend
python final_korean_api.py
# 기본 포트: 5000, CORS 활성화
```

- 터미널 2: 프론트엔드(React)
```bash
cd frontend/react-app
npm start
# 기본 포트: 3000
```

프론트에서 `http://localhost:5000`의 API를 호출합니다.

### 주요 API
- **GET** `/api/search?keyword=<검색어>`
  - 설명: 에브리타임 강의실에서 `<검색어>`로 강의를 검색하여 프론트 친화적 스키마로 반환
  - 요청 예:
```bash
curl "http://localhost:5000/api/search?keyword=%ED%86%B5%EA%B3%84"
```
  - 응답 예:
```json
{
  "success": true,
  "results": [
    {
      "id": 1,
      "subject": "통계학입문",
      "name": "통계학입문",
      "professor": "홍길동",
      "course_code": "CS001",
      "department": "컴퓨터공학과",
      "credits": 3,
      "rating": 4.0,
      "reviews": [],
      "tags": ["강의평", "에브리타임"],
      "ai_summary": "통계학입문 강의입니다. 홍길동 교수님이 담당하십니다.",
      "sentiment": 80,
      "raw_text": "원문 텍스트..."
    }
  ]
}
```

### 프론트엔드
- CRA 기반이며 `react-scripts start/build` 스크립트를 사용합니다.

### 벡터 파이프라인(mock)
- 목적: 실제 벡터DB 연동 전, 임베딩 업서트/검색 흐름을 검증
- 데이터: `vector_pipeline/mock_data.jsonl`
- 실행:
```bash
cd vector_pipeline
python upsert_mock.py   # mock 데이터 업서트 시뮬레이션
python query_mock.py    # 쿼리 시뮬레이션
```

### 개발 가이드
- Python 코드 스타일: 가독성 우선, 명시적 함수/변수명 사용
- 에러 처리: 초기 가드(guard clause), 불필요한 광범위 try/except 지양
- 환경 분리: `.env`로 민감정보 분리, 쿠키 파일은 레포에 포함하지 마세요

### 문제 해결
- **빈 검색 결과**
  - 쿠키 만료 가능성이 큼. `everytime_cookies.json` 재생성
  - 에브리타임 DOM 변경 시 선택자 업데이트 필요(`final_korean_api.py` 내 CSS Selector)
- **브라우저/드라이버 오류**
  - Chrome 최신/크롬드라이버 호환성 확인
  - `HEADLESS_MODE=false`로 화면 모드에서 동작 확인
- **CORS 에러**
  - 백엔드가 5000 포트에서 실행 중인지 확인, 프론트 요청 URL 점검

### 라이선스
- 내부 과제/연구 목적 사용. 외부 배포 전 서비스 약관 및 데이터 수집 정책을 준수하세요.
