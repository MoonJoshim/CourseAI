#!/usr/bin/env python3
"""새로운 강의평만 Pinecone에 업로드"""

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

# Pinecone에 없는 새로운 강의평만 추가
new_reviews = [
    # 자료구조 - SHAN GAOYANG
    {'course_name': '자료구조', 'professor': 'SHAN GAOYANG', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '판서와 설명이 체계적이라 개념 이해가 정말 잘 됩니다.', 'year': 2024},
    {'course_name': '자료구조', 'professor': 'SHAN GAOYANG', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '영어 강의지만 발음이 또렷하고 슬라이드 흐름이 좋아 따라가기 어렵지 않았습니다.', 'year': 2024},
    {'course_name': '자료구조', 'professor': 'SHAN GAOYANG', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '자료구조 기본기를 단단히 다지기 좋은 강의입니다.', 'year': 2024},
    
    # 자료구조 - HAMANDAWANA PRINCE
    {'course_name': '자료구조', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '교수님 에너지가 좋고 질문도 잘 받아주셔서 수업 몰입도가 높습니다.', 'year': 2024},
    {'course_name': '자료구조', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '영어 강의지만 설명 방식이 직관적이라 이해가 잘 됐습니다.', 'year': 2024},
    {'course_name': '자료구조', 'professor': 'HAMANDAWANA PRINCE', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '전반적으로 학생 참여를 잘 이끄는 수업입니다.', 'year': 2024},
    
    # 인공지능입문 - 고종원
    {'course_name': '인공지능입문', 'professor': '고종원', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '입문 과목답게 기본 개념을 차근차근 설명해주십니다.', 'year': 2024},
    {'course_name': '인공지능입문', 'professor': '고종원', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '난이도가 과하지 않고 이해 중심이라 부담이 적어요.', 'year': 2024},
    {'course_name': '인공지능입문', 'professor': '고종원', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '과제와 시험 모두 무난한 편입니다.', 'year': 2024},
    
    # 인공지능입문 - 강경란
    {'course_name': '인공지능입문', 'professor': '강경란', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '수업 흐름이 정돈돼 있어서 듣기 편합니다.', 'year': 2024},
    {'course_name': '인공지능입문', 'professor': '강경란', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '과제 부담이 크지 않고 설명이 깔끔한 스타일입니다.', 'year': 2024},
    {'course_name': '인공지능입문', 'professor': '강경란', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '전반적으로 무난하게 듣기 좋은 수업이었습니다.', 'year': 2024},
    
    # 인공지능입문 - 이상훈
    {'course_name': '인공지능입문', 'professor': '이상훈', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '설명이 논리적으로 잘 구성돼 있어서 개념 이해가 잘 됩니다.', 'year': 2024},
    {'course_name': '인공지능입문', 'professor': '이상훈', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '개념 전달이 명확하고 예시도 적절해서 따라가기 좋았습니다.', 'year': 2024},
    {'course_name': '인공지능입문', 'professor': '이상훈', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '인공지능 입문 과목 중 퀄리티 높은 수업입니다.', 'year': 2024},
    
    # 인공지능 - 이상훈
    {'course_name': '인공지능', 'professor': '이상훈', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 3.0, 'text': '수업 내용은 알차지만 난이도가 꽤 있습니다.', 'year': 2024},
    {'course_name': '인공지능', 'professor': '이상훈', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 3.0, 'text': '기초가 약하면 중간 이후부터 따라가기 힘들 수 있습니다.', 'year': 2024},
    {'course_name': '인공지능', 'professor': '이상훈', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 3.0, 'text': '내용은 좋지만 학점 따기는 살짝 빡센 편입니다.', 'year': 2024},
    
    # 디지털회로 - SHEN YIWEN
    {'course_name': '디지털회로', 'professor': 'SHEN YIWEN', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '회로 개념을 시각적으로 잘 풀어 설명해줍니다.', 'year': 2024},
    {'course_name': '디지털회로', 'professor': 'SHEN YIWEN', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '영어 강의임에도 불구하고 전달력이 좋은 편입니다.', 'year': 2024},
    {'course_name': '디지털회로', 'professor': 'SHEN YIWEN', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '디지털회로 처음 배우는 학생에게 추천합니다.', 'year': 2024},
    
    # 디지털회로 - 박진경
    {'course_name': '디지털회로', 'professor': '박진경', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '설명이 굉장히 꼼꼼해서 이해가 잘 됩니다.', 'year': 2024},
    {'course_name': '디지털회로', 'professor': '박진경', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '시험은 수업 내용 기반이라 복습만 해도 충분합니다.', 'year': 2024},
    {'course_name': '디지털회로', 'professor': '박진경', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '강의력, 구성 모두 만족스러웠습니다.', 'year': 2024},
    
    # 객체지향프로그래밍및실습 - 류기열 (이미 객체지향및프로그래밍실습은 있지만, 객체지향프로그래밍및실습은 다름)
    {'course_name': '객체지향프로그래밍및실습', 'professor': '류기열', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '객체지향 개념을 예제로 잘 설명해줍니다.', 'year': 2024},
    {'course_name': '객체지향프로그래밍및실습', 'professor': '류기열', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '실습 위주로 진행돼서 실무 감각도 익힐 수 있습니다.', 'year': 2024},
    {'course_name': '객체지향프로그래밍및실습', 'professor': '류기열', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '코딩 연습 많이 할 사람에게 추천합니다.', 'year': 2024},
    
    # SW산업세미나 - 강경란
    {'course_name': 'SW산업세미나', 'professor': '강경란', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '실무 관련 강연 위주라 현장감이 있습니다.', 'year': 2024},
    {'course_name': 'SW산업세미나', 'professor': '강경란', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '내용이 지루하지 않고 동기부여가 잘 됩니다.', 'year': 2024},
    {'course_name': 'SW산업세미나', 'professor': '강경란', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '부담 없이 듣기 좋으면서도 얻는 게 많은 과목입니다.', 'year': 2024},
    
    # IT전문영어 - Joseph Ball
    {'course_name': 'IT전문영어', 'professor': 'Joseph Ball', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '실생활과 전공을 연결한 영어 표현 학습이 유용합니다.', 'year': 2024},
    {'course_name': 'IT전문영어', 'professor': 'Joseph Ball', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '발음과 표현 교정 피드백이 꽤 도움이 됩니다.', 'year': 2024},
    {'course_name': 'IT전문영어', 'professor': 'Joseph Ball', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 4.0, 'text': '전공 영어 기초 다지기에 적절한 수업입니다.', 'year': 2024},
]

print(f"📤 {len(new_reviews)}개의 새로운 강의평을 Pinecone에 업로드합니다...\n")

vectors = []
for i, review in enumerate(new_reviews):
    text = review['text']
    embedding = model.encode(text).tolist()
    
    unique_string = f"{review['course_name']}_{review['professor']}_{review['semester']}_{i}_{text[:30]}"
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
