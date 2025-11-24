#!/usr/bin/env python3
"""현재 Pinecone에 있는 강의/교수 조합 확인"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
from collections import defaultdict

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX', 'courses-dev'))

results = index.query(vector=[0.0] * 768, top_k=10000, include_metadata=True)

courses_set = set()
for match in results.matches:
    meta = match.metadata
    if meta:
        key = f"{meta.get('course_name')} - {meta.get('professor')}"
        courses_set.add(key)

print("📋 현재 Pinecone에 있는 강의/교수 조합:\n")
for course in sorted(courses_set):
    print(f"  - {course}")
print(f"\n총 {len(courses_set)}개의 강의/교수 조합")

# 확인할 새로운 강의들
new_courses_to_check = [
    "자료구조 - SHAN GAOYANG",
    "자료구조 - HAMANDAWANA PRINCE",
    "인공지능입문 - 고종원",
    "인공지능입문 - 강경란",
    "인공지능입문 - 이상훈",
    "인공지능 - 이상훈",
    "디지털회로 - SHEN YIWEN",
    "디지털회로 - 박진경",
    "데이터베이스 - 정태선",
    "기계학습 - 손경아",
    "객체지향프로그래밍및실습 - 류기열",
    "SW캡스톤디자인 - 윤대균",
    "SW산업세미나 - 강경란",
    "IT전문영어 - Joseph Ball"
]

print("\n\n🔍 새로운 강의평 추가 여부 확인:\n")
for course in new_courses_to_check:
    if course in courses_set:
        print(f"  ❌ {course} - 이미 존재")
    else:
        print(f"  ✅ {course} - 추가 필요")
