# 강의평 Pinecone 업로드 스크립트

## 개요
에브리타임 API 응답 형식의 강의평 데이터를 Pinecone 벡터 데이터베이스에 저장하는 스크립트입니다.

## 설정 방법

### 1. 환경변수 설정
`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```bash
# Pinecone 연동
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX=courses-dev
```

### 2. 강의 정보 수정
`upload_reviews_to_pinecone.py` 파일의 `course_info` 딕셔너리를 수정하세요:

```python
course_info = {
    "course_name": "머신러닝",           # 강의명
    "professor": "김교수",              # 교수명
    "department": "소프트웨어학과",      # 학과
    "ai_analysis": {                   # AI 분석 결과 (선택사항)
        "has_team_project": True,
        "difficulty_level": 4,
        "workload_level": 4,
        "sentiment_score": 0.2
    }
}
```

### 3. 강의평 데이터 수정
`api_response_data` 딕셔너리에 실제 에브리타임 API 응답 데이터를 넣으세요.

## 사용법

### 기본 실행
```bash
cd /path/to/CourseAI
python scripts/upload_reviews_to_pinecone.py
```

### 실행 결과
스크립트는 다음 작업을 수행합니다:
1. VectorStore 초기화
2. 강의평 데이터 변환
3. Pinecone에 벡터 업로드
4. 인덱스 통계 출력
5. 검색 테스트 실행

## 데이터 형식

### 입력 데이터 (에브리타임 API 응답)
```json
{
    "status": "success",
    "result": {
        "articles": [
            {
                "isMine": false,
                "id": 5715392,
                "year": 2023,
                "semester": "여름",
                "text": "강의력이 좋고, 학생을 배려해줌 대신 팀 프로젝트가 있음.",
                "rate": 5,
                "posvote": 0
            }
        ]
    }
}
```

### Pinecone 저장 형식
```json
{
    "id": "머신러닝_김교수_001",
    "values": [0.1, 0.2, ...],  // 벡터 임베딩
    "metadata": {
        "course_name": "머신러닝",
        "professor": "김교수",
        "department": "소프트웨어학과",
        "semester": "2023-summer",
        "year": 2023,
        "rating": 5,
        "posvote": 0,
        "original_id": 5715392,
        "is_mine": false,
        "source": "evertime",
        "uploaded_at": "2024-01-01T00:00:00",
        "has_team_project": true,
        "difficulty_level": 4,
        "workload_level": 4,
        "sentiment_score": 0.2
    }
}
```

## 벡터 ID 생성 규칙
- 형식: `{강의명}_{교수명}_{리뷰인덱스}`
- 예시: `machine_learning_hong_gil_dong_001`, `machine_learning_hong_gil_dong_002`

## 검색 방법

### Python에서 검색
```python
from backend.models.vector_store import VectorStore

vs = VectorStore()

# 특정 강의의 강의평만 검색
results = vs.query_similar_reviews(
    "팀프로젝트가 있는 강의",
    top_k=5,
    filter_dict={"course_name": "머신러닝", "professor": "김교수"}
)

# 전체 강의평에서 검색
results = vs.query_similar_reviews("과제가 많은 강의", top_k=10)
```

## 주의사항
1. Pinecone API 키가 유효한지 확인하세요
2. 인덱스가 존재하는지 확인하세요 (없으면 자동 생성됨)
3. 강의명과 교수명은 정확히 입력하세요 (검색 시 필터링에 사용)
4. 메타데이터의 null 값은 자동으로 제거됩니다

## 문제 해결
- **인증 오류**: Pinecone API 키 확인
- **인덱스 오류**: 인덱스 이름 확인
- **임베딩 오류**: sentence-transformers 모델 다운로드 확인
- **메타데이터 오류**: null 값이 포함된 필드 확인
