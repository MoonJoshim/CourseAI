#!/usr/bin/env python3
"""
강의평 데이터를 Pinecone에 업로드하는 스크립트
에브리타임 API 응답 형식의 강의평 데이터를 벡터화하여 저장
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import hashlib

# 환경변수 로드
load_dotenv()

class VectorStore:
    """Pinecone 벡터 스토어 관리 클래스"""
    
    def __init__(self):
        """Pinecone 클라이언트 초기화"""
        # 환경변수 체크
        api_key = os.environ.get("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY 환경변수가 설정되지 않았습니다. .env 파일을 생성하고 API 키를 설정하세요.")
        
        self.pc = Pinecone(api_key=api_key)
        self.index_name = os.environ.get("PINECONE_INDEX", "courses-dev")
        self.index = self.pc.Index(self.index_name)
        
        # 임베딩 모델 초기화
        model_name = os.environ.get("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
        print(f"🧠 임베딩 모델 로딩 중... ({model_name})")
        self.embedder = SentenceTransformer(model_name)
        print(f"✅ 임베딩 모델 로드 완료: {model_name}")
        print(f"✅ VectorStore 초기화 완료 - 인덱스: {self.index_name}, 모델: {model_name}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """텍스트 리스트를 벡터로 변환"""
        embeddings = self.embedder.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def sanitize_id(self, text: str) -> str:
        """한글 등 비ASCII 문자를 안전한 ASCII ID로 변환"""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def upsert_reviews(self, review_items: List[Dict[str, Any]]) -> bool:
        """강의평 데이터를 Pinecone에 저장"""
        try:
            # 텍스트 추출 및 임베딩
            texts = [item["text"] for item in review_items]
            print(f"📝 벡터화할 텍스트 샘플: {texts[0][:50]}..." if texts else "❌ 텍스트 없음")
            vectors = self.embed_texts(texts)
            
            # Pinecone 업서트 형식으로 변환
            upsert_vectors = []
            for item, vector in zip(review_items, vectors):
                # 이미 ASCII-safe ID로 생성되었으므로 그대로 사용
                upsert_vectors.append({
                    "id": item["id"],
                    "values": vector,
                    "metadata": item["metadata"]
                })
            
            # Pinecone에 업서트
            self.index.upsert(vectors=upsert_vectors)
            print(f"✅ {len(upsert_vectors)}개 강의평을 Pinecone에 저장했습니다.")
            return True
            
        except Exception as e:
            print(f"❌ Pinecone 업서트 실패: {e}")
            return False

    def query_similar_reviews(self, query_text: str, top_k: int = 10, 
                            filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """유사한 강의평 검색"""
        try:
            # 쿼리 텍스트 임베딩
            query_vector = self.embed_texts([query_text])[0]
            
            # Pinecone 검색
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict or {}
            )
            
            # 결과 포맷팅
            similar_reviews = []
            for match in results.matches:
                similar_reviews.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            return similar_reviews
            
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return []

    def get_index_stats(self) -> Dict[str, Any]:
        """인덱스 통계 정보 조회"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            print(f"❌ 통계 조회 실패: {e}")
            return {}

def korean_to_ascii(text: str) -> str:
    """한글을 ASCII-safe 문자열로 변환"""
    # 간단한 매핑 테이블
    korean_map = {
        '기계학습': 'machine_learning',
        '손경아': 'son_kyung_ah',
        '소프트웨어학과': 'software_engineering',
        '머신러닝': 'machine_learning',
        '김교수': 'kim_professor'
    }
    
    result = text
    for korean, ascii_text in korean_map.items():
        result = result.replace(korean, ascii_text)
    
    # 나머지 한글은 해시로 변환
    if any('\uac00' <= char <= '\ud7af' for char in result):
        result = hashlib.md5(result.encode('utf-8')).hexdigest()[:8]
    
    return result

def create_review_items(api_response_data: dict, course_info: dict) -> list:
    """
    API 응답 데이터를 Pinecone 저장 형식으로 변환
    
    Args:
        api_response_data: 에브리타임 API 응답 데이터
        course_info: 강의 정보 (course_name, professor, department 등)
    
    Returns:
        list: Pinecone 저장용 리뷰 아이템 리스트
    """
    review_items = []
    articles = api_response_data.get("result", {}).get("articles", [])
    
    for idx, article in enumerate(articles):
        # 벡터 ID를 ASCII-safe로 생성
        course_name_ascii = korean_to_ascii(course_info['course_name'])
        professor_ascii = korean_to_ascii(course_info['professor'])
        review_id = f"{course_name_ascii}_{professor_ascii}_{idx:03d}"
        
        # 학기 정보 정규화
        semester = f"{article['year']}-{article['semester']}"
        if article['semester'] == "여름":
            semester = f"{article['year']}-summer"
        elif article['semester'] == "겨울":
            semester = f"{article['year']}-winter"
        
        # 메타데이터 구성 (Pinecone은 null 값 허용 안함)
        metadata = {
            "course_name": course_info["course_name"],
            "professor": course_info["professor"],
            "department": course_info["department"],
            "semester": semester,
            "year": article["year"],
            "rating": article["rate"],
            "posvote": article["posvote"],
            "original_id": article["id"],
            "is_mine": article["isMine"],
            "source": "evertime",
            "uploaded_at": datetime.now().isoformat(),
            "text": article["text"]  # 리뷰 텍스트도 메타데이터에 포함
        }
        
        # AI 분석 필드들 (하드코딩으로 설정 가능)
        if "ai_analysis" in course_info:
            ai_analysis = course_info["ai_analysis"]
            metadata.update({
                "has_team_project": ai_analysis.get("has_team_project"),
                "difficulty_level": ai_analysis.get("difficulty_level"),
                "workload_level": ai_analysis.get("workload_level"),
                "sentiment_score": ai_analysis.get("sentiment_score")
            })
        
        # 리뷰 아이템 생성
        review_item = {
            "id": review_id,
            "text": article["text"],
            "metadata": metadata
        }
        
        review_items.append(review_item)
    
    return review_items

def main():
    """메인 실행 함수"""
    print("🚀 강의평 데이터 Pinecone 업로드 시작")
    print("=" * 60)
    
    # 환경변수 로드
    load_dotenv()
    
    # 하드코딩된 강의 정보 (필요에 따라 수정)
    course_info = {
        "course_name": "기계학습",  # 강의명
        "professor": "손경아",      # 교수명
        "department": "소프트웨어학과",  # 학과
        # "ai_analysis": {  # AI 분석 결과 (선택사항)
        #     "has_team_project": True,
        #     "difficulty_level": 4,
        #     "workload_level": 4,
        #     "sentiment_score": 0.2
        # }
    }
    
    # 에브리타임 API 응답 데이터 (하드코딩)
    api_response_data = {
        "status": "success",
        "result": {
            "articles": [
                {
                    "isMine": False,
                    "id": 5715392,
                    "year": 2023,
                    "semester": "여름",
                    "text": "강의력이 좋고, 학생을 배려해줌 대신 팀 프로젝트가 있음.",
                    "rate": 5,
                    "posvote": 0
                },
                {
                    "isMine": False,
                    "id": 5530627,
                    "year": 2023,
                    "semester": "1",
                    "text": "강의력 좋음 과제가 조금 어렵긴 하지만 하면 잘 받을 수 있음",
                    "rate": 5,
                    "posvote": 0
                },
                {
                    "isMine": False,
                    "id": 5136872,
                    "year": 2022,
                    "semester": "2",
                    "text": "수업시간에 진도가 너무 빨라서 사실상 독학으로 시험 과제 준비한다고 보면됨. 시험 전 마지막 수업마다 지난학기 기출 풀어주시는데 그거 위주로 공부하면 시험은 어느정도 맞을수 있다. 팀프는 여느 팀프처럼 팀원 잘만나면 좋고 해야하는 일이 그렇게 많지는 않아서 여유롭게 할수 있음.",
                    "rate": 4,
                    "posvote": 0
                },
                {
                    "isMine": False,
                    "id": 5096462,
                    "year": 2022,
                    "semester": "2",
                    "text": "강의실 분위기를 보면 다들 노트북으로 뭔가 뚱땅뚱땅 하고 있고 강의를 듣는 사람은 별로 없다. 교수님은 교수님대로 진도를 엄청 빨리 나가신다.\n오늘 이만큼 나가야겠다 하고 정해놓은 분량이 있으신거 같고 그거 맞추려고 설명을 생략하거나, 말을 빨리해서 우다다 진도를 나가는 느낌이 없지않아 있다.\n시험 2번에 프로젝트과제와 개인과제 + Challenge로 구성되어 있어 꽤나 바쁘다.\n프로젝트 팀원 구성은 알아서 모으거나, bb를 통해 남은 사람들을 매칭해주는 시스템인데 중간에 파토나는 팀들도 있었다.\n시험의 경우 학생들의 성적 분포에 따라 난이도를 조절하시는거 같다. 평이한 수준?\n과제는 강의시간에 알려주는거에 비하면 많은걸 요구하는편",
                    "rate": 4,
                    "posvote": 6
                },
                {
                    "isMine": False,
                    "id": 4616331,
                    "year": 2022,
                    "semester": "1",
                    "text": "과제많습니다. 팀플 시간 많이뺏깁니다. 그렇지만 머신러닝이 이런거구나 하고 알아가는건 많았던것같습니다.",
                    "rate": 4,
                    "posvote": 0
                },
                {
                    "isMine": False,
                    "id": 4590857,
                    "year": 2022,
                    "semester": "1",
                    "text": "설명도 잘해주시고 하다보면 흥미도 느낄 수 있긴한데 과제랑 챌린지가 시간을 너무 많이 잡아먹음\n\n+ 팀플도 중요하긴 한데 중간기말 성적 비율이 높기 때문에 시험을 잘 봐야 성적이 잘나옴\n\nA+ 받긴 했지만 과제도 너무 많고 여유가 많지 않은 이상 다신 듣고 싶지 않은 과목이었음",
                    "rate": 5,
                    "posvote": 0
                },
                {
                    "isMine": False,
                    "id": 4579728,
                    "year": 2022,
                    "semester": "1",
                    "text": "머신러닝에 대해 하나도 모른채로 들었는데 엄청 많이 배웠다. 그리고 흥미도 생기게 해준 수업. 과제는 많지만 열심히 하면 성취도도 있고 교수님도 잘 가르치신다. 시험은 쉬운편이고 팀플 과제 모두 다 잘해야 성적 잘 나올것 같다. 성적 늦게나오는것 빼고는 정말 좋았던 수업.",
                    "rate": 5,
                    "posvote": 0
                },
                {
                    "isMine": False,
                    "id": 3653441,
                    "year": 2021,
                    "semester": "1",
                    "text": "인공 지능 들을 생각 있으면 수강 전에 들으세요 그럼 인공지능이 편해요",
                    "rate": 4,
                    "posvote": 0
                },
                {
                    "isMine": False,
                    "id": 3510001,
                    "year": 2021,
                    "semester": "1",
                    "text": "무난무난하게 듣기 좋은 과목. 인공지능 전에 들으면 좋을듯",
                    "rate": 4,
                    "posvote": 0
                },
                {
                    "isMine": False,
                    "id": 3501494,
                    "year": 2021,
                    "semester": "1",
                    "text": "엄청난 단점도 없지만 엄청난 장점도 없는 그냥 무난한 강의",
                    "rate": 4,
                    "posvote": 0
                },
                {
                    "isMine": False,
                    "id": 3255645,
                    "year": 2021,
                    "semester": "1",
                    "text": "재밌게한만큼 성취도도 좋았던지라, 비율을 어떻게 줬는지는 모르겠지만, 과제나 수업 등 배워갈 것이 많은 수업이었다. 이 수업을 듣고 나서 기계학습에 대해 더 깊은 공부를 해보려고한다.",
                    "rate": 5,
                    "posvote": 1
                }
            ]
        }
    }
    
    try:
        # VectorStore 초기화
        print("🔧 VectorStore 초기화 중...")
        vector_store = VectorStore()
        
        # 강의 정보 출력
        print(f"📚 강의 정보:")
        print(f"   - 강의명: {course_info['course_name']}")
        print(f"   - 교수명: {course_info['professor']}")
        print(f"   - 학과: {course_info['department']}")
        
        # API 응답 데이터 변환
        print("🔄 강의평 데이터 변환 중...")
        review_items = create_review_items(api_response_data, course_info)
        print(f"✅ {len(review_items)}개 강의평 데이터 변환 완료")
        
        # Pinecone에 업로드
        print("📤 Pinecone에 업로드 중...")
        success = vector_store.upsert_reviews(review_items)
        
        if success:
            print("=" * 60)
            print("🎉 강의평 데이터 업로드 완료!")
            
            # 인덱스 통계 출력
            stats = vector_store.get_index_stats()
            if stats:
                print(f"📊 인덱스 통계:")
                print(f"   - 총 벡터 수: {stats.get('total_vector_count', 'N/A')}")
                print(f"   - 벡터 차원: {stats.get('dimension', 'N/A')}")
                print(f"   - 인덱스 사용률: {stats.get('index_fullness', 'N/A')}")
            
            # 검색 테스트
            print("\n🔍 검색 테스트:")
            test_query = "팀프로젝트가 있는 강의"
            similar_reviews = vector_store.query_similar_reviews(
                test_query, 
                top_k=3,
                filter_dict={"course_name": course_info["course_name"]}
            )
            
            print(f"   쿼리: '{test_query}'")
            print(f"   결과: {len(similar_reviews)}개 유사 강의평 발견")
            for i, review in enumerate(similar_reviews, 1):
                # 메타데이터에서 텍스트 정보 출력
                metadata = review['metadata']
                course_name = metadata.get('course_name', 'Unknown')
                professor = metadata.get('professor', 'Unknown')
                rating = metadata.get('rating', 0)
                text = metadata.get('text', '')[:50] + '...' if metadata.get('text') else 'No text'
                print(f"   {i}. 점수: {review['score']:.3f} - {course_name}({professor}) 평점:{rating}")
                print(f"      내용: {text}")
                
        else:
            print("❌ 업로드 실패")
            
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
