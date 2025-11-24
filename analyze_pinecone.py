#!/usr/bin/env python3
"""Pinecone 강의평 데이터 분석"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
from collections import Counter

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX', 'courses-dev'))

print("🔍 Pinecone 강의평 데이터 분석\n")

# 모든 데이터 가져오기 (페이징)
all_data = []
try:
    # 더미 쿼리로 데이터 가져오기
    results = index.query(
        vector=[0.0] * 768,
        top_k=10000,  # 큰 숫자로 최대한 많이 가져오기
        include_metadata=True
    )
    all_data = results.matches
except Exception as e:
    print(f"❌ 데이터 조회 실패: {e}")
    exit(1)

print(f"📊 총 {len(all_data)}개의 강의평 벡터")

# 강의별 통계
courses = Counter()
professors = Counter()
ratings = []
years = Counter()
semesters = Counter()

for match in all_data:
    meta = match.metadata
    if meta:
        course_name = meta.get('course_name', 'Unknown')
        prof = meta.get('professor', 'Unknown')
        rating = meta.get('rating')
        year = meta.get('year')
        semester = meta.get('semester', 'Unknown')
        
        courses[course_name] += 1
        professors[prof] += 1
        if rating:
            ratings.append(float(rating))
        if year:
            years[int(year)] += 1
        semesters[semester] += 1

print(f"\n📚 강의별 강의평 수 (Top 10):")
for course, count in courses.most_common(10):
    print(f"  {count:3d}개 - {course}")

print(f"\n👨‍🏫 교수별 강의평 수 (Top 10):")
for prof, count in professors.most_common(10):
    print(f"  {count:3d}개 - {prof}")

if ratings:
    avg_rating = sum(ratings) / len(ratings)
    print(f"\n⭐ 평균 평점: {avg_rating:.2f} / 5.0")
    print(f"   최고 평점: {max(ratings):.1f}")
    print(f"   최저 평점: {min(ratings):.1f}")

print(f"\n📅 연도별 분포:")
for year in sorted(years.keys()):
    print(f"  {year}년: {years[year]}개")

print(f"\n📆 학기별 분포 (Top 5):")
for sem, count in semesters.most_common(5):
    print(f"  {sem}: {count}개")

# 샘플 강의평 내용 보기
print(f"\n📝 샘플 강의평 (3개):")
for i, match in enumerate(all_data[:3], 1):
    meta = match.metadata
    print(f"\n  {i}. {meta.get('course_name')} - {meta.get('professor')} ({meta.get('semester')})")
    print(f"     평점: {meta.get('rating')}/5")
    text = meta.get('text', '')
    if len(text) > 100:
        print(f"     내용: {text[:100]}...")
    else:
        print(f"     내용: {text}")
