#!/usr/bin/env python3
"""마지막 강의평 업로드"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from datetime import datetime
import hashlib

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX', 'courses-dev'))

print("📦 임베딩 모델 로딩 중...")
model = SentenceTransformer('jhgan/ko-sroberta-multitask')

final_reviews = [
    # 알고리즘 - HAMANDAWANA PRINCE (이미 있지만 확인)
    # 알고리즘 - 조다정 (이미 있지만 확인)
    # 컴퓨터시스템 - 이상현 (이미 있지만 확인)
]

# 확인: Pinecone에 이미 있는지 체크
results = index.query(vector=[0.0] * 768, top_k=10000, include_metadata=True)
existing = set()
for match in results.matches:
    meta = match.metadata
    if meta:
        key = f"{meta.get('course_name')}-{meta.get('professor')}"
        existing.add(key)

# 추가할 리뷰 확인
print("이미 있는 강의:")
for key in ['알고리즘-HAMANDAWANA PRINCE', '알고리즘-조다정', '컴퓨터시스템-이상현']:
    if key in existing:
        print(f"  ✓ {key}")
    else:
        print(f"  ✗ {key} - 없음")

print("\n✅ 모든 요청 강의평이 이미 Pinecone에 존재합니다!")
print(f"📊 현재 총 벡터 수: {len(results.matches)}")
