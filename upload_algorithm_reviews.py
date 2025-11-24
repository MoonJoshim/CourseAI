#!/usr/bin/env python3
"""알고리즘, 컴퓨터시스템 강의평 업로드"""

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

# 알고리즘, 컴퓨터시스템 강의평
new_reviews = [
    # 알고리즘 - HAMANDAWANA PRINCE
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '수업 내용은 나중에도 유익한 내용인 것 같고 시험은 진짜 과제에서 절반 이상 나옴 퀴즈도 중간중간 보는데 내용만 잘 알고 있으면 부담없이 볼 수 있음', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '시험은 과제랑 퀴즈에서 거의 대부분이 나와서 시간 없으면 두 개만 보고 가도 점수 잘 나올 듯', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '진짜 최고의 교수님 과제랑 퀴즈만 잘 풀고 중간 기말 망쳐도 기본 B 플러스는 확정 착하시고 진짜 좋음', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '과제 충분히 쉽고 시험은 퀴즈나 과제에서 많이 나와서 부담 없음 성적 잘 나옴', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '이 교수님 디화를 수강하시는 게 좋아보입니다 시험은 치트시트를 적극 활용하시고 치트시트에 고봉밥으로 적어가십시오', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '출석 널널 강의 열정 넘침 녹강도 남겨주셔서 모르는건 복습 가능', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '교수님이 친절하세요 과제 없음 조모임 없음 성적 보통', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '진도 적당하고 교수님 굉장히 친절합니다', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '녹화강의 있어서 편했음 시험도 저한테는 적절해서 할만했음', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '교수님 열정 넘치심 근데 강의력은 매우 좋다고는 못함 시험문제 예측불가능', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 3.0, 'text': '중간까지 할만함 기말범위 너무 어려움 설명 잘 못하심', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '영어 수업이라 가끔 잘 안 들릴 때는 있는데 강의력은 좋은 편', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '질문 잘 받아주시고 시험은 공부한 만큼 나옴 영어강의인데 중간 어려운 부분은 한국어로 다시 설명해주심', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': 'B만 뿔 채워주시는 듯 B+와 A 경계선 친구들이 억울해함', 'year': 2024},
    {'course_name': '알고리즘', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '강의력 보통 시험은 객관식이지만 헷갈리면 점수 박살 과제는 베릴로그 라이크한 간단한 RISC 프로세서 만드는 과제', 'year': 2024},
    
    # 알고리즘 - 조다정
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 5.0, 'text': '설명을 아주 꼼꼼하게 해주십니다 과제도 할만해요', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 5.0, 'text': '중간고사가 자료구조 수업과 매우 겹침 설명은 꼼꼼', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 5.0, 'text': '조다정 교수님 자료구조 수업이랑 매우 겹칩니다', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 5.0, 'text': '중간은 생각보다 어려웠는데 기말은 할만함 잘 가르쳐주심', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 4.0, 'text': '무난무난함 원어강의라 성적 받기 쉬움 알고리즘 지식은 많이 얻은 것 같진 않음', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 5.0, 'text': '외국인 교수님이지만 설명 천천히 잘 해주셔서 이해 쉬움', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 4.0, 'text': '증명을 잘 해야 함 뒤로 갈수록 어려워져서 중간을 잘 봐야 함', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 5.0, 'text': '잘 가르쳐주심 강의 꼼꼼히 보면 학점 나쁘지 않음 과제 거의 없음', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 4.0, 'text': '알고리즘이 아니라 수학 배우는 느낌 증명 좋아하심 시험 절대 못 맞음', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 5.0, 'text': '내용이 생소하고 영어라 이해 어려웠다는 평도 있음', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 5.0, 'text': '수업만 잘 들으면 됨 과제 1번 있었음', 'year': 2024},
    {'course_name': '알고리즘', 'professor': '조다정', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 4.0, 'text': '강의력 과제 시험 기타 별점 평가', 'year': 2024},
    
    # 컴퓨터시스템 - 이상현
    {'course_name': '컴퓨터시스템', 'professor': '이상현', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '교수님 강의에 열정적이시고 친절하세요 학생들과 소통도 많이 하려 하시고 배려해주셔서 좋아요 시험은 강노에 비해 조금 어려웠어요', 'year': 2024},
]

print(f"📤 {len(new_reviews)}개의 강의평을 Pinecone에 업로드합니다...\n")

vectors = []
for i, review in enumerate(new_reviews):
    text = review['text']
    embedding = model.encode(text).tolist()
    
    unique_string = f"{review['course_name']}_{review['professor']}_{review['semester']}_{i}_{text[:50]}"
    hash_id = hashlib.md5(unique_string.encode()).hexdigest()[:16]
    vector_id = f"review_{hash_id}"
    
    metadata = {
        'course_name': review['course_name'],
        'professor': review['professor'],
        'department': review['department'],
        'semester': review['semester'],
        'year': float(review['year']),
        'rating': float(review['rating']),
        'text': review['text'],
        'source': 'manual',
        'uploaded_at': datetime.now().isoformat()
    }
    
    vectors.append({
        'id': vector_id,
        'values': embedding,
        'metadata': metadata
    })
    
    print(f"✅ {i+1}/{len(new_reviews)}: {review['course_name']} - {review['professor']} (평점 {review['rating']})")

print(f"\n📤 Pinecone 업로드 중...")
index.upsert(vectors=vectors)
print(f"✅ 업로드 완료!\n")

stats = index.describe_index_stats()
print(f"📊 업데이트된 Pinecone 통계:")
print(f"  - 총 벡터 수: {stats.total_vector_count}")
