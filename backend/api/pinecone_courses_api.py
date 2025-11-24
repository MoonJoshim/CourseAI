#!/usr/bin/env python3
"""Pinecone 강의 데이터 API"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from collections import defaultdict

load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX = os.getenv('PINECONE_INDEX', 'courses-dev')

@app.route('/api/courses/from-pinecone', methods=['GET'])
def get_courses_from_pinecone():
    """Pinecone에서 강의 목록 가져오기 (강의평 기반으로 요약)"""
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX)
        
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
            'professors': set()
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
            courses_dict[key]['professors'].add(professor)
        
        # 강의 목록 생성
        courses = []
        for idx, (key, data) in enumerate(courses_dict.items(), 1):
            avg_rating = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else 0
            review_count = len(data['reviews'])
            
            # 최근 강의평 3개로 AI 요약 생성
            recent_reviews = data['reviews'][:3]
            ai_summary = ' '.join(recent_reviews[:2])[:150] + '...' if recent_reviews else '강의평 정보 없음'
            
            # 태그 추출 (간단한 키워드 기반)
            tags = []
            all_text = ' '.join(data['reviews'])
            if '팀플' in all_text or '팀프로젝트' in all_text:
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
        
        return jsonify({
            'success': True,
            'courses': courses,
            'total': len(courses)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/')
def index():
    return '''
    <h1>Pinecone 강의 데이터 API</h1>
    <ul>
        <li><code>GET /api/courses/from-pinecone</code> - Pinecone에서 강의 목록 가져오기</li>
    </ul>
    '''

if __name__ == '__main__':
    print("🎓 Pinecone 강의 데이터 API 서버 시작")
    print("📍 http://localhost:5004")
    app.run(debug=True, host='0.0.0.0', port=5004)
