# MongoDB 스키마 설계 문서

## 개요
에브리타임 크롤링 및 AI 챗봇 서비스를 위한 MongoDB 데이터베이스 스키마 설계입니다.

## 데이터베이스 구조

### 1. 강의 정보 (courses)

#### 1.1 Course 문서 구조
```json
{
  "_id": ObjectId,
  "course_id": "SW101",                    // 강의 고유 ID
  "course_name": "자료구조",               // 강의명
  "professor": "홍길동",                   // 교수명
  "department": "소프트웨어학과",          // 학과
  "semester": "2024-1",                   // 학기
  
  "details": {                            // 강의 상세 정보
    "attendance": "중요",                 // 출석 관련
    "exam": "중간/기말",                  // 시험 관련
    "assignment": "적당",                 // 과제 관련
    "team_project": "없음",               // 팀프로젝트 관련
    "time_slot": "월(1,2) 수(3)",        // 수업 시간
    "room": "공학관 301호",               // 강의실
    "credits": 3                          // 학점
  },
  
  "reviews": [                            // 강의평 목록
    {
      "review_id": "r-001",
      "rating": 4.5,
      "comment": "팀플은 없고 과제가 적당히 있어요...",
      "semester": "2024-1",
      "created_at": ISODate,
      "source": "evertime",
      "sentiment_score": 0.8,             // AI 감정 분석
      "has_team_project": false,          // 팀프로젝트 여부
      "difficulty_level": 3,              // 난이도 (1-5)
      "workload_level": 2                 // 과제량 (1-5)
    }
  ],
  
  "total_reviews": 15,                    // 총 리뷰 수
  "average_rating": 4.2,                  // 평균 평점
  
  "ai_summary": "팀플 없고 과제 적당한 편...", // AI 요약
  "sentiment_analysis": {                 // 감정 분석 결과
    "positive": 0.7,
    "negative": 0.1,
    "neutral": 0.2
  },
  "keywords": ["객체지향", "설계패턴"],     // 키워드
  "tags": ["노팀플", "적당한과제"],        // 태그
  
  "popularity_score": 85.5,               // 인기도 점수
  "trend_direction": "up",                // 트렌드 방향
  
  "created_at": ISODate,                  // 생성일
  "updated_at": ISODate,                  // 수정일
  "last_crawled_at": ISODate,             // 마지막 크롤링일
  "source": "evertime"                    // 데이터 출처
}
```

#### 1.2 인덱스
- `course_id` (unique)
- `course_name`
- `professor`
- `department`
- `semester`
- `average_rating`
- `created_at`
- `course_name + professor` (text search)

---

### 2. 대화 정보 (conversations)

#### 2.1 Conversation 문서 구조
```json
{
  "_id": ObjectId,
  "session_id": "sess_123456789",         // 세션 고유 ID
  "user_id": "user_001",                  // 사용자 ID (선택사항)
  
  "messages": [                           // 메시지 목록
    {
      "role": "user",                     // 메시지 역할
      "content": "노팀플 강의 추천해줘",   // 메시지 내용
      "timestamp": ISODate,               // 메시지 시간
      "function_name": null,              // 호출된 함수명
      "function_args": null,              // 함수 인자
      "function_result": null,            // 함수 결과
      "tokens_used": 15,                  // 사용된 토큰 수
      "model_used": "gpt-4"               // 사용된 모델
    },
    {
      "role": "assistant",
      "content": "노팀플 강의를 추천해드릴게요...",
      "timestamp": ISODate,
      "function_name": "search_lecture",
      "function_args": {"keyword": "노팀플"},
      "function_result": {"success": true, "results": [...]},
      "tokens_used": 150,
      "model_used": "gpt-4"
    }
  ],
  
  "total_messages": 10,                   // 총 메시지 수
  "title": "강의 추천 상담",              // 대화 제목
  "tags": ["강의추천", "노팀플"],         // 대화 태그
  "category": "course_recommendation",    // 대화 카테고리
  
  "total_tokens_used": 1500,              // 총 사용 토큰 수
  "function_calls_count": 3,              // 함수 호출 횟수
  
  "is_active": true,                      // 활성 세션 여부
  "created_at": ISODate,                  // 생성일
  "updated_at": ISODate,                  // 수정일
  "last_activity": ISODate                // 마지막 활동일
}
```

#### 2.2 인덱스
- `session_id` (unique)
- `user_id`
- `created_at`
- `is_active`

---

### 3. 사용자 정보 (users)

#### 3.1 UserProfile 문서 구조
```json
{
  "_id": ObjectId,
  "user_id": "user_001",                  // 사용자 고유 ID
  "name": "김학생",                       // 이름
  "major": "소프트웨어학과",              // 전공
  "semester": 7,                          // 학기
  "student_id": "2020123456",             // 학번
  
  "gpa": 3.45,                           // GPA
  "total_credits": 98,                   // 총 이수 학점
  "required_credits": 130,               // 졸업 필요 학점
  
  "preferences": {                        // 사용자 선호도
    "interests": ["프론트엔드", "웹개발"], // 관심 분야
    "preferred_difficulty": "medium",     // 선호 난이도
    "avoid_team_projects": true,          // 팀프로젝트 회피 여부
    "preferred_professors": ["김교수"],   // 선호 교수
    "time_preferences": ["오전", "오후"]   // 시간대 선호도
  },
  
  "bookmarked_courses": ["SW101", "SW102"], // 북마크한 강의
  "search_history": ["데이터베이스", "웹프로그래밍"], // 검색 기록
  "chat_sessions": ["sess_001", "sess_002"], // 챗봇 세션
  
  "total_searches": 25,                   // 총 검색 횟수
  "total_chat_messages": 50,              // 총 챗봇 메시지 수
  
  "created_at": ISODate,                  // 계정 생성일
  "updated_at": ISODate,                  // 마지막 수정일
  "last_login": ISODate,                  // 마지막 로그인
  "is_active": true                       // 계정 활성 상태
}
```

#### 3.2 인덱스
- `user_id` (unique)
- `student_id`
- `created_at`

---

### 4. 사용자 활동 로그 (user_activities)

#### 4.1 UserActivity 문서 구조
```json
{
  "_id": ObjectId,
  "user_id": "user_001",                  // 사용자 ID
  "activity_type": "search",              // 활동 유형
  "activity_data": {                      // 활동 데이터
    "keyword": "데이터베이스",
    "results_count": 5,
    "response_time_ms": 1200
  },
  "ip_address": "192.168.1.100",          // IP 주소
  "user_agent": "Mozilla/5.0...",         // 사용자 에이전트
  "timestamp": ISODate,                   // 활동 시간
  "session_id": "sess_123456789"          // 세션 ID
}
```

#### 4.2 인덱스
- `user_id`
- `activity_type`
- `timestamp`
- `user_id + timestamp` (복합)

---

### 5. 분석 데이터

#### 5.1 검색 분석 (search_analytics)
```json
{
  "_id": ObjectId,
  "date": ISODate,                        // 분석 날짜
  "total_searches": 150,                  // 총 검색 수
  "unique_keywords": 45,                  // 고유 키워드 수
  "popular_keywords": [                   // 인기 키워드
    {"keyword": "데이터베이스", "count": 25},
    {"keyword": "웹프로그래밍", "count": 20}
  ],
  "avg_results_per_search": 3.2,          // 검색당 평균 결과 수
  "no_result_searches": 5,                // 결과 없는 검색 수
  "hourly_searches": {                    // 시간대별 검색 수
    "09": 15, "10": 20, "11": 25
  }
}
```

#### 5.2 강의 분석 (course_analytics)
```json
{
  "_id": ObjectId,
  "course_id": "SW101",                   // 강의 ID
  "date": ISODate,                        // 분석 날짜
  "total_views": 120,                     // 총 조회 수
  "unique_viewers": 85,                   // 고유 조회자 수
  "search_appearances": 45,               // 검색 결과 노출 수
  "search_clicks": 12,                    // 검색 결과 클릭 수
  "click_through_rate": 0.27,             // 클릭률
  "bookmarks": 8,                         // 북마크 수
  "new_reviews": 3,                       // 신규 리뷰 수
  "avg_rating": 4.2                       // 평균 평점
}
```

#### 5.3 챗봇 분석 (chat_analytics)
```json
{
  "_id": ObjectId,
  "date": ISODate,                        // 분석 날짜
  "total_conversations": 25,              // 총 대화 수
  "total_messages": 150,                  // 총 메시지 수
  "avg_messages_per_conversation": 6.0,   // 대화당 평균 메시지 수
  "unique_users": 20,                     // 고유 사용자 수
  "returning_users": 8,                   // 재방문 사용자 수
  "function_calls": 45,                   // 함수 호출 수
  "function_success_rate": 0.95,          // 함수 성공률
  "popular_functions": [                  // 인기 함수
    {"function": "search_lecture", "count": 30},
    {"function": "compare_lectures", "count": 15}
  ],
  "avg_response_time_ms": 2500,           // 평균 응답 시간
  "max_response_time_ms": 8000,           // 최대 응답 시간
  "total_tokens_used": 15000,             // 총 사용 토큰 수
  "avg_tokens_per_message": 100           // 메시지당 평균 토큰 수
}
```

#### 5.4 시스템 메트릭 (system_metrics)
```json
{
  "_id": ObjectId,
  "timestamp": ISODate,                   // 측정 시간
  "crawling_status": "active",            // 크롤링 상태
  "last_crawl_time": ISODate,             // 마지막 크롤링 시간
  "crawl_success_rate": 0.95,             // 크롤링 성공률
  "total_crawled_courses": 1250,          // 총 크롤링된 강의 수
  "api_requests_per_minute": 45,          // 분당 API 요청 수
  "api_error_rate": 0.02,                 // API 에러율
  "avg_api_response_time_ms": 800,        // 평균 API 응답 시간
  "db_connection_count": 5,               // DB 연결 수
  "db_query_time_ms": 50,                 // DB 쿼리 시간
  "memory_usage_mb": 512.5,               // 메모리 사용량
  "cpu_usage_percent": 25.3               // CPU 사용률
}
```

---

## 데이터 관계도

```
Users (1) ←→ (N) Conversations
Users (1) ←→ (N) UserActivities
Courses (1) ←→ (N) Reviews
Courses (1) ←→ (N) CourseAnalytics
Conversations (1) ←→ (N) Messages
```

## 성능 최적화

### 1. 인덱스 전략
- **복합 인덱스**: 자주 함께 조회되는 필드들
- **텍스트 인덱스**: 강의명, 교수명 검색용
- **TTL 인덱스**: 활동 로그 자동 삭제용

### 2. 샤딩 전략
- **수평 샤딩**: 사용자 ID 기준
- **수직 샤딩**: 분석 데이터 별도 컬렉션

### 3. 캐싱 전략
- **Redis**: 인기 검색어, 세션 데이터
- **메모리**: 자주 조회되는 강의 정보

## 데이터 마이그레이션

### 1. 초기 데이터 설정
```javascript
// 인덱스 생성
db.courses.createIndex({"course_id": 1}, {"unique": true})
db.conversations.createIndex({"session_id": 1}, {"unique": true})
db.users.createIndex({"user_id": 1}, {"unique": true})

// TTL 인덱스 (30일 후 자동 삭제)
db.user_activities.createIndex({"timestamp": 1}, {"expireAfterSeconds": 2592000})
```

### 2. 데이터 검증
```javascript
// 스키마 검증 함수
function validateCourse(course) {
  return course.course_id && 
         course.course_name && 
         course.professor &&
         course.average_rating >= 0 && 
         course.average_rating <= 5;
}
```

## 보안 고려사항

1. **데이터 암호화**: 민감한 사용자 정보
2. **접근 제어**: 역할 기반 권한 관리
3. **감사 로그**: 모든 데이터 변경 추적
4. **개인정보 보호**: GDPR 준수

## 모니터링

1. **성능 모니터링**: 쿼리 성능, 인덱스 사용률
2. **용량 모니터링**: 컬렉션 크기, 디스크 사용량
3. **에러 모니터링**: 연결 실패, 쿼리 오류
4. **비즈니스 메트릭**: 사용자 활동, 인기 강의
