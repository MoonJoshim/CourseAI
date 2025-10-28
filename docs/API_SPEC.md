# 에브리타임 크롤링 API 명세서

## 개요
에브리타임 강의평 크롤링 및 AI 챗봇 서비스를 제공하는 REST API입니다.

## 기본 정보
- **Base URL**: `http://localhost:5002` (강의 검색), `http://localhost:5003` (AI 챗봇)
- **Content-Type**: `application/json`
- **인코딩**: UTF-8

---

## 1. 강의 검색 API (Lecture API)

### 1.1 강의 검색
**엔드포인트**: `GET /api/search`

**설명**: 에브리타임에서 강의명 또는 교수명으로 강의를 검색합니다.

**요청 파라미터**:
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| keyword | string | O | 검색할 강의명 또는 교수명 |

**요청 예시**:
```http
GET /api/search?keyword=데이터베이스
GET /api/search?keyword=김교수
```

**응답 형식**:
```json
{
  "keyword": "데이터베이스",
  "results": [
    {
      "subject": "데이터베이스시스템",
      "professor": "김교수",
      "rating": 4.2,
      "reviewCount": 15,
      "reviews": [
        {
          "rating": 4.5,
          "comment": "팀플은 없고 과제가 적당히 있어요. 시험 난이도는 중간.",
          "semester": "2024-1"
        }
      ],
      "details": {
        "attendance": "중요",
        "exam": "중간/기말",
        "assignment": "적당",
        "teamProject": "없음"
      }
    }
  ],
  "count": 1
}
```

**에러 응답**:
```json
{
  "error": "검색어를 입력해주세요"
}
```

### 1.2 MongoDB 헬스체크
**엔드포인트**: `GET /api/health/db`

**설명**: MongoDB 연결 상태를 확인합니다.

**응답 형식**:
```json
{
  "ok": true,
  "result": {
    "ok": 1
  }
}
```

**에러 응답**:
```json
{
  "ok": false,
  "error": "Connection failed"
}
```

---

## 2. AI 챗봇 API (AI API)

### 2.1 AI 챗봇 대화
**엔드포인트**: `POST /api/chat`

**설명**: OpenAI GPT-4를 이용한 강의 상담 챗봇입니다.

**요청 본문**:
```json
{
  "message": "노팀플 강의 추천해줘",
  "history": [
    {
      "user": "안녕하세요",
      "assistant": "안녕하세요! 강의 관련 질문이 있으시면 언제든 물어보세요."
    }
  ]
}
```

**응답 형식**:
```json
{
  "response": "노팀플 강의를 추천해드릴게요! 다음과 같은 강의들이 있습니다...",
  "timestamp": "2024-01-15T10:30:00Z",
  "function_called": "search_lecture"
}
```

**에러 응답**:
```json
{
  "error": "메시지를 입력해주세요"
}
```

### 2.2 챗봇 테스트
**엔드포인트**: `GET /api/chat/test`

**설명**: 챗봇 API 상태를 확인합니다.

**응답 형식**:
```json
{
  "message": "챗봇 API가 정상 작동 중입니다!",
  "test_queries": [
    "데이터베이스 강의평 알려줘",
    "컴공 추천 과목은?",
    "웹프로그래밍이랑 모바일프로그래밍 중에 뭐가 나을까?"
  ],
  "endpoints": {
    "chat": "POST /api/chat",
    "test": "GET /api/chat/test"
  }
}
```

### 2.3 MongoDB 헬스체크 (AI API)
**엔드포인트**: `GET /api/health/db`

**설명**: AI API 서버의 MongoDB 연결 상태를 확인합니다.

**응답 형식**: 강의 검색 API와 동일

---

## 3. 데이터 모델

### 3.1 강의 정보 (Course)
```json
{
  "subject": "string",           // 강의명
  "professor": "string",         // 교수명
  "rating": "number",            // 평점 (0.0-5.0)
  "reviewCount": "number",       // 리뷰 개수
  "reviews": [                   // 강의평 목록
    {
      "rating": "number",        // 개별 평점
      "comment": "string",       // 리뷰 내용
      "semester": "string"       // 학기
    }
  ],
  "details": {                   // 상세 정보
    "attendance": "string",      // 출석 관련
    "exam": "string",           // 시험 관련
    "assignment": "string",     // 과제 관련
    "teamProject": "string"     // 팀프로젝트 관련
  }
}
```

### 3.2 대화 메시지 (Message)
```json
{
  "message": "string",           // 사용자 메시지
  "history": [                   // 대화 히스토리
    {
      "user": "string",          // 사용자 메시지
      "assistant": "string"      // AI 응답
    }
  ]
}
```

---

## 4. 에러 코드

| HTTP 상태 코드 | 설명 |
|---------------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (필수 파라미터 누락 등) |
| 500 | 서버 내부 오류 (크롤링 실패, 로그인 실패 등) |

---

## 5. 사용 예시

### 5.1 프론트엔드에서 강의 검색
```javascript
const searchCourses = async (keyword) => {
  try {
    const response = await fetch(`http://localhost:5002/api/search?keyword=${encodeURIComponent(keyword)}`);
    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    return data.results;
  } catch (error) {
    console.error('검색 오류:', error);
    throw error;
  }
};
```

### 5.2 프론트엔드에서 AI 챗봇 사용
```javascript
const sendChatMessage = async (message, history = []) => {
  try {
    const response = await fetch('http://localhost:5003/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        history
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('챗봇 오류:', error);
    throw error;
  }
};
```

---

## 6. 환경 설정

### 6.1 필수 환경변수
```bash
# 에브리타임 로그인
EVERYTIME_ID=your_evertime_id
EVERYTIME_PASSWORD=your_evertime_password

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# MongoDB (선택사항)
MONGO_URI=mongodb://root:example@localhost:27017/crawller?authSource=admin
```

### 6.2 서버 실행
```bash
# 강의 검색 API 서버 (포트 5002)
python backend/api/lecture_api.py

# AI 챗봇 API 서버 (포트 5003)
python backend/api/ai_api.py
```

---

## 7. 주의사항

1. **크롤링 제한**: 에브리타임 사이트의 이용약관을 준수해야 합니다.
2. **로그인 세션**: 30분마다 자동으로 재로그인됩니다.
3. **reCAPTCHA**: 로그인 시 수동으로 해결해야 할 수 있습니다.
4. **API 키**: OpenAI API 키가 필요합니다.
5. **CORS**: 프론트엔드에서 접근 시 CORS가 허용되어 있습니다.

---

## 8. 업데이트 이력

- **v1.0.0** (2024-01-15): 초기 API 명세 작성
  - 강의 검색 API 구현
  - AI 챗봇 API 구현
  - MongoDB 헬스체크 추가
