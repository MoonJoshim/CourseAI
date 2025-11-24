# CourseAI

강의평 기반 AI 강의 추천 및 분석 플랫폼

## 프로젝트 개요

CourseAI는 실제 수강생들의 강의평 데이터(380개 이상)를 기반으로 AI 기반 강의 추천, 검색, 분석을 제공하는 완성된 풀스택 웹 애플리케이션입니다. RAG(Retrieval-Augmented Generation) 기술을 활용하여 벡터 검색 기반의 정확한 강의 정보를 실시간으로 제공합니다.

## 주요 기능

### 1. 전공과목 강의평 조회 ✅
- 40개 이상의 실제 강의 데이터 제공
- 380개 이상의 실제 수강생 강의평 기반 평가
- 학과별, 교수별, 평점별 실시간 필터링
- 태그 기반 빠른 검색 (노팀플, 과제많음, 성적잘줌, 쉬움)
- 평점, 리뷰 수, 난이도, 과제량, 학점 관대함 등 상세 정보
- 수강생 평가 요약 AI 분석 제공

### 2. 개설과목 현황 ✅
- 2025-2학기 전체 개설과목 조회 (3047개 과목)
- 전공필수 / 전공선택 / 교양선택 탭 분류
- 강의 시간, 교수, 학점, 강의실 등 상세 정보
- 그리드/리스트 뷰 전환 기능
- 실시간 검색 및 정렬

### 3. AI 채팅 ✅
- RAG 기반 강의평 AI 어시스턴트 완전 구현
- 자연어 질문으로 강의 추천 및 비교
- Pinecone 벡터 검색으로 가장 관련성 높은 강의평 근거 제시
- Google Gemini API 활용
- 채팅 히스토리 관리
- 추천 프롬프트 제공

### 4. 학점 계산기 ✅
- 학기별 수강 계획 입력 및 저장
- 실시간 예상 평균 학점 계산
- 현재 학점, 목표 학점 대비 갭 분석
- 졸업 필요 학점 140학점 기준 진행률 시각화
- C+ 이하 과목 자동 감지 및 재수강 우선순위 추천
- 로컬 스토리지 자동 저장

### 5. 회원 관리 ✅
- Google OAuth 로그인 연동
- 64개 전공 선택 지원
- 프로필 정보 수정 기능
- 에브리타임 계정 연동 입력 (선택사항)

## 기술 스택

### Frontend
- **React 18** - 메인 프레임워크
- **Tailwind CSS** - 스타일링
- **Lucide React** - 아이콘
- **Context API** - 상태 관리
- **Vercel** - 배포 플랫폼

### Backend
- **Python 3.11** - 메인 언어
- **Flask** - API 서버
- **Selenium** - 웹 크롤링
- **BeautifulSoup4** - HTML 파싱

### AI/ML
- **Google Gemini API** - LLM
- **Sentence Transformers** - 임베딩 모델 (jhgan/ko-sroberta-multitask)
- **Pinecone** - 벡터 데이터베이스

### Database
- **MongoDB** - 강의 데이터 저장
- **Pinecone** - 강의평 벡터 검색

## 아키텍처

```
Frontend (React)
    ↓
Backend API Servers
    ├─ lecture_api.py (Port 5002) - 강의 검색/조회
    └─ ai_api.py (Port 5003) - AI 채팅
    ↓
Data Sources
    ├─ MongoDB - 강의 데이터
    ├─ Pinecone - 강의평 벡터 (380개)
    └─ Excel - 개설과목 현황
```

## 설치 및 실행

### 사전 준비
- Python 3.11+
- Node.js 18+
- Chrome (Selenium용)

### 1. 저장소 클론
```bash
git clone https://github.com/MoonJoshim/CourseAI.git
cd CourseAI
```

### 2. 백엔드 설정
```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정 (.env 파일 생성)
# PINECONE_API_KEY, GEMINI_API_KEY 등 설정 필요
```

### 3. 프론트엔드 설정
```bash
cd frontend/react-app
npm install

# 환경변수 설정
echo "REACT_APP_BACKEND_URL=http://localhost:5002" > .env
echo "REACT_APP_AI_API_URL=http://localhost:5003" >> .env
```

### 4. 실행
**터미널 1 - 강의 검색 API:**
```bash
cd backend
python api/lecture_api.py
# http://localhost:5002
```

**터미널 2 - AI 채팅 API:**
```bash
cd backend
python api/ai_api.py
# http://localhost:5003
```

**터미널 3 - 프론트엔드:**
```bash
cd frontend/react-app
npm start
# http://localhost:3000
```

## 주요 API 엔드포인트

### 강의 검색 API (Port 5002)
- `GET /api/search?keyword=강의명` - 강의 검색
- `GET /api/software-courses` - 개설과목 현황
- `GET /api/courses/from-pinecone` - Pinecone 강의 목록

### AI 채팅 API (Port 5003)
- `POST /api/chat` - RAG 기반 대화
  ```json
  {
    "message": "노팀플 강의 추천해줘",
    "history": [],
    "top_k": 5
  }
  ```

## 데이터

### Pinecone 벡터 DB
- **총 벡터 수**: 380개
- **차원**: 768
- **주요 강의**: 
  - 데이터베이스 (70개)
  - 컴퓨터네트워크 (54개)
  - 기계학습 (38개)
  - 알고리즘 (27개)
  - 객체지향프로그래밍 (28개)
  - 기타 다수

### 개설과목 현황
- **총 과목 수**: 3047개
- **학기**: 2025-2
- **학과**: 소프트웨어학과 중심

## 배포

### 프론트엔드 (Vercel)
- **URL**: https://courseai-frontend.vercel.app
- **자동 배포**: main 브랜치 push 시

### 백엔드 (VM)
- **IP**: 34.56.30.245
- **Port**: 5002 (강의 검색), 5003 (AI 채팅)

### 환경변수 설정 (Vercel)
```
REACT_APP_BACKEND_URL=http://34.56.30.245:5002
REACT_APP_AI_API_URL=http://34.56.30.245:5003
```

## 프로젝트 구조

```
CourseAI/
├── frontend/react-app/          # React 프론트엔드
│   ├── src/
│   │   ├── components/          # 공통 컴포넌트
│   │   ├── pages/               # 페이지 컴포넌트
│   │   ├── context/             # Context API
│   │   ├── constants/           # 상수 (전공 목록 등)
│   │   └── data/                # 정적 데이터
│   └── package.json
├── backend/                     # Flask 백엔드
│   ├── api/                     # API 서버
│   │   ├── lecture_api.py       # 강의 검색 API
│   │   └── ai_api.py            # AI 채팅 API
│   ├── crawler/                 # 크롤러
│   └── models/                  # 데이터 모델
├── config/                      # 설정 파일
├── course/                      # 강의 데이터
├── pipeline/                    # 벡터 파이프라인
├── .env                         # 환경변수
└── requirements.txt             # Python 의존성
```

## 개발 가이드

### 강의평 데이터 추가
```python
# 1. 강의평 데이터 준비
reviews = [
    {
        'course_name': '강의명',
        'professor': '교수명',
        'rating': 5.0,
        'text': '강의평 내용',
        'semester': '2024-2',
        'year': 2024
    }
]

# 2. Pinecone 업로드 스크립트 실행
python upload_new_reviews.py

# 3. 프론트엔드 데이터 재생성
python generate_pinecone_courses.py
```

### 코드 스타일
- **React**: 함수형 컴포넌트, Hooks 사용
- **Python**: PEP 8 준수
- **커밋 메시지**: 한글 한 줄 요약

## 주요 기능 상세

### RAG 기반 AI 채팅
1. 사용자 질문 입력
2. 질문을 벡터로 임베딩
3. Pinecone에서 유사한 강의평 검색 (top_k=5)
4. 검색된 강의평을 컨텍스트로 Gemini API 호출
5. 근거 있는 답변 생성

### 강의 검색 시스템
- MongoDB와 Pinecone을 활용한 하이브리드 검색
- 강의명, 교수명, 학과명, 과목코드 실시간 검색
- 평점, 리뷰 수, 가나다순 다중 정렬 지원
- 태그 기반 스마트 필터링

### 학점 계산 시스템
- 브라우저 로컬 스토리지 자동 저장
- 실시간 GPA 계산 및 시뮬레이션
- 재수강 시 학점 향상 효과 분석
- C+ 이하 과목 우선순위 추천 알고리즘

## 라이선스

교육 및 연구 목적으로 사용하세요.

## 기여

이슈와 PR은 언제든 환영합니다!

## 문의

- GitHub: https://github.com/MoonJoshim/CourseAI
- Email: mmmm27@example.com

