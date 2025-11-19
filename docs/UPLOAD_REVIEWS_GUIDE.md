# 강의평 데이터 Pinecone 업로드 가이드

에브리타임 API에서 강의평 데이터를 가져와 Pinecone 벡터 데이터베이스에 업로드하는 스크립트 사용 가이드입니다.

## 목차

1. [사전 준비](#사전-준비)
2. [스크립트 설정](#스크립트-설정)
3. [실행 방법](#실행-방법)
4. [응답 구조 확인](#응답-구조-확인)
5. [문제 해결](#문제-해결)
6. [FAQ](#faq)

---

## 사전 준비

### 1. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성하거나 수정합니다:

```bash
# Pinecone 설정
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX=your_index_name  # 예: courses-dev, courses-reviews
PINE_NS=_default_  # 또는 특정 namespace (선택사항, 기본값: _default_)

# 임베딩 모델 설정 (선택사항)
EMBEDDING_MODEL=intfloat/multilingual-e5-base  # 기본값 사용 시 생략 가능
```

### 2. 필요한 패키지 설치

```bash
pip install pinecone-client sentence-transformers python-dotenv
```

또는 프로젝트 requirements.txt 사용:

```bash
pip install -r requirements.txt
```

---

## 스크립트 설정

`scripts/upload_reviews_to_pinecone.py` 파일을 열어 다음 세 가지를 수정합니다.

### 1단계: 강의 정보 수정 (필수)

**위치**: 440-444줄

```python
course_info = {
    "course_name": "기계학습",  # ← 실제 강의명으로 변경
    "professor": "손경아",      # ← 실제 교수명으로 변경
    # "department": "소프트웨어학과",  # 선택사항: 학과명
}
```

**예시**:
```python
course_info = {
    "course_name": "데이터베이스",
    "professor": "홍길동",
    "department": "컴퓨터공학과",
}
```

### 2단계: 한글-ASCII 매핑 확인/추가 (선택, 권장)

**위치**: 160-166줄

기존 데이터와 ID 형식을 일치시키려면 `korean_map`에 매핑을 추가합니다:

```python
korean_map = {
    '기계학습': 'machine_learning',  # 이미 있음
    '손경아': 'son_kyung_ah',        # 이미 있음
    # 새로 추가할 강의/교수명
    '데이터베이스': 'database',
    '홍길동': 'hong_gil_dong',
}
```

**중요**: 
- 매핑이 없으면 MD5 해시로 변환되어 ID가 달라질 수 있습니다
- 기존 데이터와 일관성을 유지하려면 매핑을 추가하세요
- ID 형식: `{강의명_ascii}_{교수명_ascii}_{시퀀스번호}` (예: `machine_learning_son_kyung_ah_001`)

### 3단계: cURL 명령어 수정 (필수)

**위치**: 447-463줄

브라우저에서 복사한 cURL 명령어를 입력합니다:

```python
curl_command = """curl 'https://api.everytime.kr/find/lecture/article/list' \\
  -H 'accept: application/json, text/plain, */*' \\
  -H 'content-type: application/x-www-form-urlencoded' \\
  -b '쿠키값' \\
  --data-raw 'lectureId=강의ID&limit=20&offset=0&sort=id'"""
```

**주의사항**:

1. **쿠키 (`-b` 옵션)**: 
   - `etsid` 쿠키가 만료되면 새로 복사해야 합니다
   - 브라우저 개발자 도구 → Network 탭 → 요청 → Headers → Cookie에서 복사

2. **lectureId**: 
   - 해당 강의의 실제 ID로 변경
   - 에브리타임 웹사이트에서 강의 상세 페이지 URL 확인

3. **offset**: 
   - 처음부터 가져오려면 `0`으로 시작
   - 다음 배치: `offset=20`, `offset=40` 등으로 증가

4. **limit**: 
   - 한 번에 가져올 개수 (최대값 확인 필요, 보통 20-100)

**cURL 명령어 복사 방법**:

1. Chrome/Edge: 개발자 도구 (F12) → Network 탭
2. 에브리타임에서 강의평 페이지 로드
3. `find/lecture/article/list` 요청 찾기
4. 우클릭 → Copy → Copy as cURL

---

## 실행 방법

### 기본 실행

```bash
# 프로젝트 루트 디렉토리에서 실행
cd /Users/seohyun/Desktop/CourseAI
python scripts/upload_reviews_to_pinecone.py
```

### 실행 과정

스크립트는 다음 순서로 실행됩니다:

1. **API 호출**: cURL 명령어로 에브리타임 API에서 강의평 데이터 가져오기
2. **VectorStore 초기화**: Pinecone 연결 및 임베딩 모델 로드
3. **기존 데이터 조회**: 중복 검증을 위해 기존 데이터 확인
4. **데이터 변환**: API 응답을 Pinecone 형식으로 변환
   - ID 생성: `machine_learning_son_kyung_ah_001` 형식
   - 시퀀스 번호: 기존 데이터 다음 번호부터 자동 할당
   - 중복 검증: `original_id`와 `text`로 중복 확인
5. **Pinecone 업로드**: 벡터화하여 Pinecone에 저장

### 실행 결과 예시

```
🚀 강의평 데이터 Pinecone 업로드 시작
============================================================
🌐 cURL 명령어 실행 중...
✅ cURL 응답 받기 완료
   응답 최상위 키: ['result', 'status']
   result 키: ['articles', 'total']
   articles 개수: 20
   첫 번째 article 키: ['id', 'year', 'semester', 'text', 'rate', ...]
🔧 VectorStore 초기화 중...
🧠 임베딩 모델 로딩 중... (intfloat/multilingual-e5-base)
✅ 임베딩 모델 로드 완료
✅ VectorStore 초기화 완료 - 인덱스: courses-dev, 모델: intfloat/multilingual-e5-base

📚 강의 정보:
   - 강의명: 기계학습
   - 교수명: 손경아

🔄 강의평 데이터 변환 중...
🔍 기존 데이터 조회 중 (중복 검증)...
   기존 ID 개수: 2
📝 20개의 articles 처리 중...
⚠️  3번째 article 중복 (original_id: 5715392), 건너뜀
⚠️  총 1개의 중복 강의평 건너뜀
✅ 19개 강의평 데이터 변환 완료 (새로 추가될 데이터)

📤 Pinecone에 업로드 중...
📝 벡터화할 텍스트 샘플: 강의력이 좋고, 학생을 배려해줌...
✅ 19개 강의평을 Pinecone에 저장했습니다. (namespace: _default_)

============================================================
🎉 강의평 데이터 업로드 완료!

📊 인덱스 통계:
   - 총 벡터 수: 21
   - 벡터 차원: 768
   - 인덱스 사용률: 0.001
```

---

## 응답 구조 확인

스크립트는 다양한 응답 형태를 자동으로 처리합니다:

- `{"result": {"articles": [...]}}`
- `{"articles": [...]}`
- `{"data": {"articles": [...]}}`

각 article에서 다음 필드를 찾습니다:

- `id` → `article_id` (original_id로 저장)
- `year` → `year`
- `semester` → `semester`
- `text` → `text` (강의평 내용)
- `rate` → `rating`

**필드명이 다른 경우**: 스크립트의 `create_review_items` 함수에서 필드명을 수정하세요.

---

## 문제 해결

### 1. 쿠키 만료 오류

**증상**: API 호출 실패 또는 인증 오류

**해결**:
1. 브라우저에서 에브리타임에 로그인
2. 개발자 도구 → Network 탭
3. 강의평 페이지 새로고침
4. `find/lecture/article/list` 요청 찾기
5. Headers → Cookie에서 최신 쿠키 복사
6. 스크립트의 `curl_command`에서 `-b` 부분 교체

### 2. API 응답 오류

**증상**: "articles를 찾을 수 없습니다" 메시지

**해결**:
1. 실행 시 출력된 "응답 최상위 키" 확인
2. 응답 구조가 예상과 다른지 확인
3. `create_review_items` 함수에서 응답 구조에 맞게 수정

**예시**:
```python
# 응답이 {"data": {"items": [...]}} 형태인 경우
articles = api_response_data["data"].get("items", [])
```

### 3. 중복 데이터가 계속 저장됨

**증상**: 같은 강의평이 여러 번 저장됨

**해결**:
1. `check_duplicates=True` 확인
2. 기존 데이터가 올바른 namespace에 있는지 확인
3. `original_id` 필드가 메타데이터에 포함되어 있는지 확인

### 4. ID 형식이 기존과 다름

**증상**: `machine_learning_son_kyung_ah_001` 대신 해시값이 사용됨

**해결**:
1. `korean_map`에 해당 강의명/교수명 매핑 추가
2. 매핑 형식: `'한글명': 'ascii_이름'`

### 5. 벡터 차원 불일치 오류

**증상**: "Vector dimension 384 does not match the dimension of the index 768"

**해결**:
1. `.env` 파일에 `EMBEDDING_MODEL=intfloat/multilingual-e5-base` 설정
2. Pinecone 인덱스 차원이 768인지 확인
3. 저장 시와 검색 시 같은 임베딩 모델 사용 확인

### 6. Namespace 오류

**증상**: 데이터를 찾을 수 없음

**해결**:
1. `.env` 파일에 `PINE_NS` 설정 확인
2. 저장 시와 검색 시 같은 namespace 사용 확인
3. `_default_` namespace 사용 시 환경변수 생략 가능

---

## FAQ

### Q1: 여러 강의를 연속으로 업로드하려면?

**A**: 스크립트를 여러 번 실행하되, 매번 다음을 변경:
1. `course_info` (강의명, 교수명)
2. `curl_command` (lectureId, 쿠키)
3. 필요시 `korean_map` 추가

### Q2: 모든 강의평을 가져오려면?

**A**: `offset`을 증가시키며 여러 번 호출:

```python
# 1차 실행: offset=0
--data-raw 'lectureId=2265164&limit=20&offset=0&sort=id'

# 2차 실행: offset=20
--data-raw 'lectureId=2265164&limit=20&offset=20&sort=id'

# 3차 실행: offset=40
--data-raw 'lectureId=2265164&limit=20&offset=40&sort=id'

# ... (응답이 없을 때까지 반복)
```

또는 스크립트를 수정하여 반복 실행하도록 구현할 수 있습니다.

### Q3: 중복 검증을 비활성화하려면?

**A**: `create_review_items` 호출 시 `check_duplicates=False` 설정:

```python
review_items = create_review_items(
    api_response_data, 
    course_info, 
    vector_store,
    namespace=namespace,
    check_duplicates=False  # 중복 검증 비활성화
)
```

### Q4: 다른 namespace에 저장하려면?

**A**: `.env` 파일에 `PINE_NS=원하는_namespace` 설정하거나, 스크립트에서 직접 지정:

```python
namespace = "ajou-2024_fall"  # 특정 namespace 지정
```

### Q5: 필드명이 다르면?

**A**: `create_review_items` 함수의 351-355줄에서 필드명 수정:

```python
# 예: rate 대신 rating을 사용하는 경우
rate = article.get("rating")  # rate → rating으로 변경
```

### Q6: 임베딩 모델을 변경하려면?

**A**: `.env` 파일에 `EMBEDDING_MODEL` 설정:

```bash
# E5 모델 (768차원) - 권장
EMBEDDING_MODEL=intfloat/multilingual-e5-base

# 다른 모델 사용 시
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # 384차원
```

**주의**: Pinecone 인덱스 차원과 일치해야 합니다.

---

## 추가 팁

### 1. 배치 처리 스크립트 작성

여러 강의를 한 번에 처리하려면:

```python
courses = [
    {"course_name": "기계학습", "professor": "손경아", "lectureId": "2265164"},
    {"course_name": "데이터베이스", "professor": "홍길동", "lectureId": "2265165"},
]

for course in courses:
    # course_info, curl_command 업데이트
    # 스크립트 실행
    pass
```

### 2. 로그 확인

실행 중 출력되는 로그를 확인하여:
- 응답 구조 파악
- 중복 데이터 확인
- 오류 원인 파악

### 3. 테스트 실행

처음에는 `limit=1`로 설정하여 작은 데이터로 테스트:

```python
--data-raw 'lectureId=2265164&limit=1&offset=0&sort=id'
```

---

## 지원

문제가 발생하면 다음을 확인하세요:

1. 환경변수 설정 (`.env` 파일)
2. 쿠키 유효성
3. Pinecone 인덱스 설정
4. 실행 로그의 디버깅 정보

추가 도움이 필요하면 프로젝트 이슈를 생성하거나 개발팀에 문의하세요.

