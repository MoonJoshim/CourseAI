#!/usr/bin/env python3
"""새로운 강의평 데이터를 Pinecone에 업로드"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from datetime import datetime
import hashlib

load_dotenv()

# Pinecone 초기화
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX', 'courses-dev'))

# 임베딩 모델 로드
print("📦 임베딩 모델 로딩 중...")
model = SentenceTransformer('jhgan/ko-sroberta-multitask')

# 새로운 강의평 데이터
new_reviews = [
    # 객체지향프로그래밍및실습 - 오윤진
    {'course_name': '객체지향프로그래밍및실습', 'professor': '오윤진', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 4.0, 'text': '처음 수업하시는거 치고 괜찮았음 캡프 과목 자체가 쉽지 않은듯', 'year': 2024},
    {'course_name': '객체지향프로그래밍및실습', 'professor': '오윤진', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 5.0, 'text': '교수님의 캡프실이 이번년도에 처음 열렸다고 알고 있는데 때문에 기출이 없어서 난항을 겪었던 거 같습니다 교수님의 컴프실 수업도 들었던 학생이라면 컴프실 수업과 문제의 형태가 다르다는 것을 알고 계셨으면 합니다 컴프실은 이론 위주의 문제가 꽤나 많이 출제되는 편인데 캡프실은 이론보다는 손코딩의 비중이 매우 커집니다 때문에 비주얼 스튜디오의 자동 완성 기능을 꺼놓고 공부하면 도움이 많이 되는 것 같습니다 사소한 부분이 기억이 안나 시험을 망치는 경우가 많은 것 같습니다 저도 이런 경우로 인해 평균보다 시험을 못쳤다가 기말 때 끌어올려 겨우 에이를 받았습니다 개인적으로 프로그래밍 트랙 소프트웨어 복전을 할 계획의 학생이라면 일학년 이학기 때 수강하시는걸 추천드립니다 이후 수업에 큰 도움이 됩니다', 'year': 2024},
    
    # 객체지향프로그래밍및실습 - SHAN GAOYANG
    {'course_name': '객체지향프로그래밍및실습', 'professor': 'SHAN GAOYANG', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '최고의 강의 수업 자료도 좋고 교수님도 열정적으로 강의하시고 질문하면 자세히 가르쳐주시려고 노력하심', 'year': 2024},
    {'course_name': '객체지향프로그래밍및실습', 'professor': 'SHAN GAOYANG', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '하나라도 더 알려주려고 노력 많이 하십니다 질문도 잘 받아주시고 다 좋았어요', 'year': 2024},
    {'course_name': '객체지향프로그래밍및실습', 'professor': 'SHAN GAOYANG', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '수업 내용이 명확하고 이해하기 쉽게 설명해 주셨고 학생들이 질문할 때마다 친절하고 자세히 답변해 주셨어요 교수님 덕분에 자바에 대한 흥미와 이해도가 많이 높아졌어요 정말 훌륭한 교수님이십니다', 'year': 2024},
    {'course_name': '객체지향프로그래밍및실습', 'professor': 'SHAN GAOYANG', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '솔직히 이번에 처음 열린 수업이라서 시험 방법이나 과제는 계속 바뀔 것 같음 그런데 교수님이 정말 좋은 분이시고 학생 생각해 주시는게 보여서 더 나아지기만 할듯 자바 노베가 듣기 좋고 조금 배웠던 사람도 들을만함', 'year': 2024},
    {'course_name': '객체지향프로그래밍및실습', 'professor': 'SHAN GAOYANG', 'department': '소프트웨어학과', 'semester': '2024-2', 'rating': 5.0, 'text': '교수님이 매우 친절하시고 수강생들을 모두 이해시키려고 노력하신다 강의자료도 도움이 많이 되었고 한국어도 잘하셔서 알아듣는데 불편함은 전혀 없었다 실습이나 과제도 복습 틈틈이 하는 사람들에게는 크게 어렵지 않은 수준 이때까지 들은 프로그래밍 수업 중에서 가장 이해가 잘 되었고 자바에 흥미를 가질 수 있게 된 아주 만족스러운 수업이었다', 'year': 2024},
    
    # 객체지향및프로그래밍실습 - YARED
    {'course_name': '객체지향및프로그래밍실습', 'professor': 'YARED', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 2.0, 'text': '강의는 안 듣고 독학했더니 그래도 학점은 잘 주십니다 강의는 정말 힘듭니다', 'year': 2024},
    {'course_name': '객체지향및프로그래밍실습', 'professor': 'YARED', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 1.0, 'text': '최악의 강의 과제는 무슨 프로젝트 하는줄 알겠다 쓰레기 같은 과제에 강노는 베껴다 읽기만 하면서 제일 짜증나는건 강노를 안 올려줘서 학생들이 사진으로 수업시간에 찍고 있는데 그래도 이주 지나서 올려주더라 재수강으로 양학하는 사람들이나 진짜 배울거 다 배워서 백엔드 프론트엔드 다 할 줄 아는 사람들이 있는지 과제로 백엔드 프론트엔드 에이피아이 활용하는게 나와서 그걸로 웹페이지 만들라 하고있네 말이 되냐 시험도 보는데 이딴걸 조별과제로 내는게 그러면서 실습 과제는 매번 내는 쓰레기 수업', 'year': 2024},
    {'course_name': '객체지향및프로그래밍실습', 'professor': 'YARED', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 2.0, 'text': '성적 너그러움 시험 쉬움 실습 개 쉬움 프로젝트 좀 힘든데 지피티 있으면 뚝딱임 배운거 없음', 'year': 2024},
    {'course_name': '객체지향및프로그래밍실습', 'professor': 'YARED', 'department': '소프트웨어학과', 'semester': '2024-1', 'rating': 1.0, 'text': '파이썬이랑 씨 씨 정도만 아는 상태에서 자바는 처음으로 해봤는데 독학으로 중간 기말 합해서 십칠인가 보면 시험 자체는 그냥 처음부터 혼자 하는거라는데 전체 깔아두고 하면 할만합니다 저는 개인적으로 원래 수업을 잘 듣지 않는 편이라 이런 방식을 선호하는 사람만 하면 괜찮을 것 같기는 하네요 아니라면 이 수업은 피하는게 맞다고 생각합니다 왜냐면 전반적으로 그냥 무대뽀로 밀어붙인다는 느낌이 많았습니다 강의자료나 팀 과제라던가 실습시간에 내주는 과제라던가 굉장히 어려웠고 답답한게 많았지만 성적은 또 생각보다 잘 나오는 것 같습니다 순수하게 코딩 베이스가 있고 성적만 받으면 된다는 분들께만 권하고 싶습니다', 'year': 2024},
    
    # 객체지향및프로그래밍실습 - PAUL RAJIB
    {'course_name': '객체지향및프로그래밍실습', 'professor': 'PAUL RAJIB', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 2.0, 'text': '수업이 어떤가를 떠나서 나처럼 영어 못하는 사람한테는 인도식 영어 수업은 정말 최악이었음 그래도 수업 자체의 난이도는 괜찮았던 기억이 있음', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': 'PAUL RAJIB', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 2.0, 'text': '학점은 결론적으로 잘 받았지만 과제에서 제시한 부분이 뭔지 이해하기 어려운 경우가 많았고 영어를 이해하기 어려워서 독학으로 공부를 하게 되었습니다', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': 'PAUL RAJIB', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 2.0, 'text': '밑에 말대로 학점 에이를 사십칠퍼나 줘서 에이플 꺼억 했습니다 강의는 발음을 어찌어찌하면 들을만 할 것 같고 메일 피드백도 생각보다 빨랐습니다', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': 'PAUL RAJIB', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 1.0, 'text': '강의 들자마자 지난 날의 선택을 후회함 에이비 비율 사십칠프로라고 메일 답장 주셨는데 삼프로 왜 안 채우는지 의문이 든다 시험들이 쉽다 매주 한번 당일 제출해야 하는 코딩 문제 올라옴', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': 'PAUL RAJIB', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 3.0, 'text': '알아들을 수 없는 교수님의 발음과 떨어지는 피피티 가독성 어느샌가 구글링으로 대신 공부하는 자신을 발견할 수 있습니다', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': 'PAUL RAJIB', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 1.0, 'text': '개오바임 못 알아듣겠음 학점이라도 잘 주길', 'year': 2023},
    
    # 객체지향및프로그래밍실습 - 오상은
    {'course_name': '객체지향및프로그래밍실습', 'professor': '오상은', 'department': '소프트웨어학과', 'semester': '2023-1', 'rating': 5.0, 'text': '교수님이 정말 똑똑하시고 자세하게 알려주려고 노력하심 자바 처음 배웠는데 실습 과제도 크게 어렵지는 않았음 조교가 별로라는 말이 있었는데 나는 반반이라고 생각함 정말로 비양심적이거나 띠꺼운 말투는 아니였지만 엄청 친절하다는 느낌도 아니였음 중간 기말고사는 난이도가 중중상 정도라고 생각함 나는 실습 만점 중간고사는 십에서 십오등 기말고사는 일등 해서 학점은 잘 받았다 열심히 공부한 만큼 점수가 잘 나온다 팀플이 있는데 조원을 너무 잘 만나서 같이 잘 마무리해서 다행이었다', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': '오상은', 'department': '소프트웨어학과', 'semester': '2023-1', 'rating': 4.0, 'text': '복수전공하는 문과였고 솔직히 중간 기말은 뒤에서 십등 정도 했는데 팀플 진짜 욕만 먹으려고 전공보다 열심히 참여했고 좋은 분 만나서 지유아이까지 얼추 해서 제출했더니 재수강 면했습니당 교수님 감사합니다', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': '오상은', 'department': '소프트웨어학과', 'semester': '2023-1', 'rating': 5.0, 'text': '중요한 내용이나 모르고 지나칠 부분까지 자세히 알려주시고 교수님도 친절하십니다 추천 또 추천', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': '오상은', 'department': '소프트웨어학과', 'semester': '2023-1', 'rating': 5.0, 'text': '정말 만족스러운 수업 교수님의 너그러움에 감탄하고 갑니다', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': '오상은', 'department': '소프트웨어학과', 'semester': '2023-1', 'rating': 5.0, 'text': '재수강이었는데 그 전 교수님이랑은 비교도 안 될 정도로 꼼꼼하게 잘 가르쳐주신다', 'year': 2023},
    
    # 객체지향및프로그래밍실습 - 류기열
    {'course_name': '객체지향및프로그래밍실습', 'professor': '류기열', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 4.0, 'text': '교수님께서 유쾌하십니다 강의력은 잘 모르겠습니다', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': '류기열', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 5.0, 'text': '스스로 자바 공부함 수업중에 중요하다고 하시는 부분 잘 듣고 시험보면 좋을듯', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': '류기열', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 4.0, 'text': '자바를 해 본 적이 없는 상태로 수강했는데 얻어가는 게 많았음 교수님께서 사투리 쓰셔서 외국인이 알아듣기에 많이 어려웠음 사투리를 많이 못 들어본 유학생 친구들에게는 추천하지 않습니다 매주 실습이 있는데 수업에 다뤘던 개념을 복습하는 정도임 시험은 두번 있는데 개념을 잘 이해하면 쉽게 풀 수 있음 수업하면서 중요하다고 강조하시는 부분들을 열심히 공부하면 좋은 점수가 나올 수 있음', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': '류기열', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 1.0, 'text': '강의력 보통 말은 알아듣기 쉽지 않아서 개인적으로 공부하는게 더 나을 수도 있음 과제들이랑 교수님이 중요하다고 했던 것들을 꼭 외워가면 시험은 어느 정도 맞출 수 있음', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': '류기열', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 1.0, 'text': '드럽게 빡셈 초보자는 이해 불가능한 수준 그냥 다른 교수님 들으셈', 'year': 2023},
    {'course_name': '객체지향및프로그래밍실습', 'professor': '류기열', 'department': '소프트웨어학과', 'semester': '2023-2', 'rating': 4.0, 'text': '교수님 발음이 많이 뭉개지시는 편이라 강의 듣기 쉽지 않았습니다 매주 실습 나가는거 따로 공부하고 실습 과제 완성했어요 실습이 개념을 잘 이해할 수 있도록 설계되어 있어서 도움 많이 되었습니다 실습 열심히 하시면 시험에도 많은 도움 돼요', 'year': 2023},
]

print(f"📤 {len(new_reviews)}개의 강의평을 Pinecone에 업로드합니다...\n")

# 벡터 생성 및 업로드
vectors = []
for i, review in enumerate(new_reviews):
    # 임베딩 생성
    text = review['text']
    embedding = model.encode(text).tolist()
    
    # ASCII 전용 Vector ID 생성 (해시 사용)
    unique_string = f"{review['course_name']}_{review['professor']}_{review['semester']}_{i}"
    hash_id = hashlib.md5(unique_string.encode()).hexdigest()[:16]
    vector_id = f"review_{hash_id}"
    
    # 메타데이터
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

# Pinecone에 업로드
print(f"\n📤 Pinecone 업로드 중...")
index.upsert(vectors=vectors)
print(f"✅ 업로드 완료!\n")

# 통계 확인
stats = index.describe_index_stats()
print(f"📊 업데이트된 Pinecone 통계:")
print(f"  - 총 벡터 수: {stats.total_vector_count}")
print(f"  - 차원: {stats.dimension}")
