# 에브리타임 강의평 크롤러

아주대학교 에브리타임에서 강의평을 자동으로 수집하고 검색할 수 있는 웹 애플리케이션입니다.

## 📁 프로젝트 구조

```
crawller/
├── src/                          # 소스 코드
│   ├── crawler/                  # 크롤링 모듈
│   │   ├── __init__.py
│   │   └── evertime_crawler.py   # 에브리타임 크롤러 클래스
│   ├── api/                      # API 서버
│   │   └── lecture_crawler_api.py # Flask API 서버
│   └── frontend/                 # 프론트엔드
│       └── lecture_search.html   # 강의평 검색 웹페이지
├── tests/                        # 테스트 파일
│   ├── simple_login_test.py      # 로그인 테스트
│   ├── get_lecture_info.py       # 강의 정보 수집 테스트
│   ├── get_page_html.py          # 페이지 HTML 수집 테스트
│   └── test_login.py             # 추가 로그인 테스트
├── scripts/                      # 실행 스크립트
│   ├── start_api.py              # API 서버 시작
│   ├── start_frontend.sh         # 프론트엔드 서버 시작
│   └── main.py                   # 메인 실행 스크립트
├── config/                       # 설정 파일
│   ├── config.py                 # 애플리케이션 설정
│   └── env.example               # 환경변수 템플릿
├── data/                         # 크롤링된 데이터
├── logs/                         # 로그 파일
├── venv/                         # Python 가상환경
├── requirements.txt              # Python 의존성
├── .gitignore                    # Git 무시 파일
└── README.md                     # 프로젝트 문서
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp config/env.example .env
# .env 파일을 편집하여 에브리타임 로그인 정보 입력
```

### 2. 서버 실행

```bash
# API 서버 시작 (포트 5002)
python scripts/start_api.py

# 프론트엔드 서버 시작 (포트 8000)
./scripts/start_frontend.sh
```

### 3. 사용법

1. 브라우저에서 `http://localhost:8000/src/frontend/lecture_search.html` 접속
2. 강의명 입력 (예: "실전코딩", "데이터베이스", "웹프로그래밍")
3. 검색 결과에서 모든 강의평을 평점순으로 확인

## 📊 지원하는 과목

- **실전코딩 1** (최재영 교수) - ⭐ 4.50
- **데이터베이스** (김영수 교수) - ⭐ 3.8
- **자료구조** (박민수 교수) - ⭐ 4.2
- **운영체제** (이정민 교수) - ⭐ 3.9
- **웹프로그래밍** (최현우 교수) - ⭐ 4.6
- **알고리즘** (강태호 교수) - ⭐ 3.7

## 🔧 주요 기능

- ✅ **실시간 크롤링**: 에브리타임에서 실시간으로 강의평 수집
- ✅ **모의 데이터**: 빠른 테스트를 위한 6개 과목 모의 데이터
- ✅ **평점순 정렬**: 모든 강의평을 평점 높은 순으로 표시
- ✅ **부분 검색**: 과목명 또는 교수명으로 부분 검색 가능
- ✅ **반응형 UI**: Tailwind CSS 기반 깔끔한 인터페이스

## 🛠️ 기술 스택

- **Backend**: Python, Flask, Selenium, BeautifulSoup4
- **Frontend**: HTML, JavaScript, Tailwind CSS
- **Database**: 파일 기반 데이터 저장
- **Crawling**: Selenium WebDriver + Chrome

## 📝 API 엔드포인트

- `GET /api/search?keyword=강의명` - 강의평 검색 (모의 데이터 + 실제 크롤링)
- `GET /api/crawl?keyword=강의명` - 실제 크롤링만 수행 (느림)

## ⚠️ 주의사항

- 에브리타임 로그인 정보가 필요합니다
- Chrome 브라우저가 설치되어 있어야 합니다
- 실제 크롤링은 시간이 오래 걸릴 수 있습니다 (10-30초)
- 과도한 크롤링은 서버에 부하를 줄 수 있으니 적절히 사용해주세요

## 📄 라이선스

이 프로젝트는 교육 목적으로만 사용되어야 합니다.