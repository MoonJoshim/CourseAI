# 프로젝트 개요

에브리타임 강의평 데이터를 수집하고, 시각화하는 Python + Flask + Selenium 기반 웹크롤링 프로젝트입니다.

### 목적

* 에브리타임 사이트에서 강의평 정보를 자동으로 수집
* 수집한 데이터를 웹 인터페이스로 검색 및 조회 가능
* 강의평 평점, 리뷰, 교수 정보 등을 체계적으로 관리

### 주요 기능

* 자동 로그인: 에브리타임 계정으로 자동 로그인
* 강의 검색: 과목명, 교수명으로 강의 검색
* 강의평 수집: 각 강의의 모든 리뷰 데이터 수집
* 웹 대시보드: 직관적인 웹 인터페이스로 데이터 조회
* 실시간 크롤링: API를 통한 실시간 데이터 수집

## 프로젝트 구조

```
crawller/
├── src/                          
│   ├── crawler/                  
│   │   ├── __init__.py
│   │   └── evertime_crawler.py      
│   ├── api/                      
│   │   └── lecture_crawler_api.py   
│   └── frontend/                 
│       └── lecture_search.html      
├── tests/                        
│   ├── simple_login_test.py         
│   ├── get_lecture_info.py          
│   ├── get_page_html.py             
│   └── test_login.py                
├── scripts/                      
│   ├── start_api.py                 
│   ├── start_frontend.sh            
│   └── main.py                      
├── config/                       
│   ├── config.py                    
│   └── env.example                  
├── data/                         
│   ├── raw_page.html                
│   └── lecture_detail.html          
├── logs/                         
├── venv/                         
└── 루트 파일들
    ├── README.md                    
    ├── requirements.txt             
    ├── .env                         
    └── .gitignore                   
```

## 빠른 시작

### 1. 사전 준비

```bash
# Python 3.9+ 필요
python --version

# Chrome 브라우저 설치 확인
google-chrome --version
```

### 2. 프로젝트 설치

```bash
git clone <repository-url>
cd crawller

python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는 venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp config/env.example .env
vim .env
```

`.env` 파일 예시:

```env
EVERYTIME_ID=your_evertime_id
EVERYTIME_PASSWORD=your_evertime_password
HEADLESS_MODE=false
DELAY_BETWEEN_REQUESTS=2.0
LOG_LEVEL=INFO
```

### 4. 실행 방법

#### 방법 1: 간편 실행 (추천)

```bash
python scripts/start_api.py
./scripts/start_frontend.sh
# 브라우저에서 접속: http://localhost:8000/src/frontend/lecture_search.html
```

#### 방법 2: 개별 실행

```bash
cd src/api
python lecture_crawler_api.py

python -m http.server 8000
```

#### 방법 3: 테스트 실행

```bash
python tests/simple_login_test.py
python tests/get_lecture_info.py
```

## 기술 스택

### Backend

* Python 3.9+
* Selenium 4.15.2
* BeautifulSoup4 4.12.2
* Flask 3.0.0
* Requests 2.31.0

### Frontend

* HTML5
* Tailwind CSS
* Vanilla JavaScript

### Tools & Libraries

* python-dotenv
* webdriver-manager
* pandas
* loguru
* flask-cors

## 사용법

### 1. 웹 대시보드

1. `http://localhost:8000/src/frontend/lecture_search.html` 접속
2. 강의명/교수명 입력 후 검색
3. 리뷰 확인

### 2. API 직접 호출

```bash
curl "http://localhost:5002/api/search?keyword=실전코딩"
curl "http://localhost:5002/api/crawl?keyword=데이터베이스"
```

### 3. Python 코드 활용

```python
from src.crawler.evertime_crawler import EverytimeCrawler

crawler = EverytimeCrawler()

if crawler.login():
    reviews = crawler.get_course_reviews("실전코딩")
    print(f"수집된 리뷰: {len(reviews)}개")

crawler.close()
```

## 설정 옵션

### config/config.py

```python
HEADLESS_MODE = False
DELAY_BETWEEN_REQUESTS = 2.0
IMPLICIT_WAIT = 10

DATA_DIR = 'data'
COURSES_FILE = 'courses.csv'
REVIEWS_FILE = 'reviews.csv'
```

## 데이터 구조

### 강의 정보

```json
{
  "subject": "실전코딩 1",
  "professor": "홍길동",
  "rating": 4.2,
  "reviewCount": 15,
  "details": {
    "attendance": "출석체크안함",
    "exam": "중간고사없음",
    "assignment": "과제많음",
    "teamProject": "팀플있음"
  }
}
```

### 리뷰 정보

```json
{
  "rating": 4.5,
  "comment": "정말 유익한 강의였습니다.",
  "semester": "2024년 1학기"
}
```

## 주의사항

### 법적 고지

* 교육 및 연구 목적 외 사용 금지
* 에브리타임 서비스 약관 준수
* 서버에 부하를 주지 않도록 주의
* 개인정보 보호 필수

### 보안

* `.env` 비공개 유지
* 계정정보 안전하게 관리
* 요청 주기 조절

### 문제 해결

```bash
pip install --upgrade webdriver-manager

# 로그인 실패 시
# 1. .env 계정 정보 확인
# 2. 에브리타임 사이트 접속 가능 여부 확인
# 3. 캡차 여부 확인

lsof -ti:5002 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

## 개발 모드

```bash
pip install pytest black flake8

black src/ tests/
flake8 src/ tests/
pytest tests/
```

디버깅:

```bash
export LOG_LEVEL=DEBUG
export HEADLESS_MODE=false
```

## 향후 계획

* [ ] 더 많은 대학 사이트 지원
* [ ] DB 연동 (SQLite/PostgreSQL)
* [ ] 시각화 차트 추가
* [ ] 강의평 감정 분석
* [ ] 모바일 UI 개선
* [ ] Docker 컨테이너화
* [ ] CI/CD 파이프라인 구축

## 라이선스

이 프로젝트는 교육 목적입니다. 상업적 사용은 금지합니다.

## 문의

프로젝트 관련 문의는 이슈로 등록해주세요.

---

**빠른 실행 명령어**

```bash
python scripts/start_api.py & ./scripts/start_frontend.sh
open http://localhost:8000/src/frontend/lecture_search.html
```
