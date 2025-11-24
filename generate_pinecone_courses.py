#!/usr/bin/env python3
"""Pinecone 데이터를 프론트엔드용 강의 목록으로 변환"""

import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone
from collections import defaultdict

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX', 'courses-dev'))

# 모든 강의평 벡터 가져오기
results = index.query(
    vector=[0.0] * 768,
    top_k=10000,
    include_metadata=True
)

# 강의별로 그룹화
courses_dict = defaultdict(lambda: {
    'reviews': [],
    'ratings': [],
    'semesters': set(),
})

for match in results.matches:
    meta = match.metadata
    if not meta:
        continue
        
    course_name = meta.get('course_name', 'Unknown')
    professor = meta.get('professor', 'Unknown')
    rating = meta.get('rating', 0)
    semester = meta.get('semester', '')
    text = meta.get('text', '')
    
    key = f"{course_name}_{professor}"
    courses_dict[key]['course_name'] = course_name
    courses_dict[key]['professor'] = professor
    courses_dict[key]['department'] = meta.get('department', '소프트웨어학과')
    courses_dict[key]['reviews'].append(text)
    courses_dict[key]['ratings'].append(float(rating))
    courses_dict[key]['semesters'].add(semester)

# 강의 목록 생성
courses = []
for idx, (key, data) in enumerate(courses_dict.items(), 1):
    avg_rating = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else 0
    review_count = len(data['reviews'])
    
    # 최근 강의평으로 AI 요약 생성
    recent_reviews = data['reviews'][:3]
    ai_summary = ' '.join(recent_reviews[:2])[:150] + '...' if recent_reviews else '강의평 정보 없음'
    
    # 태그 추출
    tags = []
    all_text = ' '.join(data['reviews'])
    if '팀플' in all_text:
        if '없' in all_text or '노팀플' in all_text:
            tags.append('노팀플')
        else:
            tags.append('팀플있음')
    if '과제' in all_text:
        if '많' in all_text:
            tags.append('과제많음')
        else:
            tags.append('적당한과제')
    if '꿀강' in all_text or '쉬' in all_text:
        tags.append('쉬움')
    if '성적' in all_text and '잘' in all_text:
        tags.append('성적잘줌')
    
    courses.append({
        'id': idx,
        'courseCode': f'SCE{300 + idx}',
        'name': data['course_name'],
        'professor': data['professor'],
        'department': data['department'],
        'credits': 3,
        'rating': round(avg_rating, 1),
        'reviewCount': review_count,
        'popularity': min(100, review_count * 3),
        'tags': tags[:4] if tags else ['강의평있음'],
        'semester': max(data['semesters']) if data['semesters'] else '2024-2',
        'timeSlot': '-',
        'room': '-',
        'aiSummary': ai_summary,
        'sentiment': int(avg_rating * 20),
        'difficulty': 3,
        'workload': 3,
        'gradeGenerosity': int(avg_rating),
        'bookmarked': False,
        'trend': 'up' if avg_rating >= 4.0 else 'down',
        'keywords': []
    })

# 평점 높은 순으로 정렬
courses.sort(key=lambda x: x['rating'], reverse=True)

# JSON 파일로 저장
output_file = 'frontend/react-app/src/data/pinecone_courses.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(courses, f, ensure_ascii=False, indent=2)

print(f"✅ {len(courses)}개의 강의 데이터를 {output_file}에 저장했습니다!")
