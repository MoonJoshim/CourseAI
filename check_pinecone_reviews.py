#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX = os.getenv('PINECONE_INDEX', 'courses-dev')

if not PINECONE_API_KEY:
    print("❌ PINECONE_API_KEY not set")
    sys.exit(1)

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

# 데이터베이스 강의평 조회
print("🔍 Pinecone에서 '데이터베이스' 강의평 조회 중...\n")

results = index.query(
    vector=[0.0] * 768,
    top_k=1000,
    include_metadata=True
)

# 데이터베이스 강의 필터링
db_reviews = []
for match in results.matches:
    meta = match.metadata
    if not meta:
        continue
    
    course_name = meta.get('course_name', '').strip()
    if '데이터베이스' in course_name or 'database' in course_name.lower():
        db_reviews.append({
            'id': match.id,
            'course_name': course_name,
            'professor': meta.get('professor', ''),
            'rating': meta.get('rating', 0),
            'semester': meta.get('semester', ''),
            'text': meta.get('text', '')[:200] if meta.get('text') else '',
            'uploaded_at': meta.get('uploaded_at', ''),
        })

print(f"✅ 총 {len(db_reviews)}개의 데이터베이스 강의평 발견\n")

# 조현석 교수 강의평
cho_reviews = [r for r in db_reviews if '조현석' in r['professor']]
print(f"📚 조현석 교수님 강의평: {len(cho_reviews)}개\n")

for i, review in enumerate(cho_reviews[:10], 1):
    print(f"{i}. ID: {review['id']}")
    print(f"   강의명: {review['course_name']}")
    print(f"   교수: {review['professor']}")
    print(f"   평점: {review['rating']}")
    print(f"   학기: {review['semester']}")
    print(f"   업로드: {review['uploaded_at']}")
    print(f"   내용: {review['text']}")
    print()

# 모든 데이터베이스 교수 목록
professors = set(r['professor'] for r in db_reviews if r['professor'])
print(f"\n📋 데이터베이스 강의 교수 목록: {', '.join(sorted(professors))}")

# API 테스트
print("\n" + "="*60)
print("🧪 API 엔드포인트 테스트")
print("="*60)

import requests
try:
    r = requests.get('http://127.0.0.1:5002/api/reviews/from-pinecone', 
                    params={'course_name': '데이터베이스', 'professor': '조현석', 'limit': 5},
                    timeout=10)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Success: {data.get('success')}")
        print(f"Total: {data.get('total', 0)}")
        reviews = data.get('reviews', [])
        print(f"Reviews returned: {len(reviews)}")
        for i, rev in enumerate(reviews[:3], 1):
            print(f"\n  {i}. Rating: {rev.get('rating')}, Semester: {rev.get('semester')}")
            print(f"     Text: {rev.get('text', '')[:100]}...")
    else:
        print(f"Error: {r.text[:500]}")
except Exception as e:
    print(f"❌ API 테스트 실패: {e}")

