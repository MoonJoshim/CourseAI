#!/usr/bin/env python3
"""
강의평 데이터를 Pinecone에 업로드하는 스크립트
에브리타임 API 응답 형식의 강의평 데이터를 벡터화하여 저장
"""

import os
import sys
import json
import subprocess
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

def execute_curl_command(curl_command: str) -> dict:
    """
    cURL 명령어를 실행하고 JSON 응답을 반환
    
    Args:
        curl_command: 실행할 cURL 명령어 문자열
    
    Returns:
        dict: JSON 응답 데이터
    """
    try:
        print(f"🌐 cURL 명령어 실행 중...")
        print(f"   명령어: {curl_command[:100]}...")
        
        # cURL 명령어를 쉘에서 실행
        result = subprocess.run(
            curl_command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        
        # JSON 응답 파싱
        response_data = json.loads(result.stdout)
        print(f"✅ cURL 응답 받기 완료 (상태: {response_data.get('status', 'unknown')})")
        
        return response_data
        
    except subprocess.CalledProcessError as e:
        print(f"❌ cURL 명령어 실행 실패: {e}")
        print(f"   에러 출력: {e.stderr}")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 실패: {e}")
        if 'result' in locals():
            print(f"   응답 내용: {result.stdout[:200]}...")
        raise

def create_review_items(api_response_data: dict, course_info: dict) -> list:
    """
    API 응답 데이터를 Pinecone 저장 형식으로 변환
    articles에서 id, year, semester, text, rate만 추출
    
    Args:
        api_response_data: 에브리타임 API 응답 데이터
        course_info: 강의 정보 (course_name, professor 필수)
    
    Returns:
        list: Pinecone 저장용 리뷰 아이템 리스트
    """
    review_items = []
    articles = api_response_data.get("result", {}).get("articles", [])
    
    print(f"📝 {len(articles)}개의 articles 처리 중...")
    
    for idx, article in enumerate(articles):
        # 필요한 필드만 추출: id, year, semester, text, rate
        article_id = article.get("id")
        year = article.get("year")
        semester = article.get("semester")
        text = article.get("text", "")
        rate = article.get("rate")
        
        # 필수 필드 검증
        if None in [article_id, year, semester, rate]:
            print(f"⚠️  {idx}번째 article에서 필수 필드 누락, 건너뜀")
            continue
        
        # 벡터 ID를 ASCII-safe로 생성
        course_name_ascii = korean_to_ascii(course_info['course_name'])
        professor_ascii = korean_to_ascii(course_info['professor'])
        review_id = f"{course_name_ascii}_{professor_ascii}_{article_id}"
        
        # 학기 정보 정규화
        semester_normalized = f"{year}-{semester}"
        if semester == "여름":
            semester_normalized = f"{year}-summer"
        elif semester == "겨울":
            semester_normalized = f"{year}-winter"
        
        # 메타데이터 구성 (필수 필드만 포함)
        metadata = {
            "course_name": course_info["course_name"],
            "professor": course_info["professor"],
            "semester": semester_normalized,
            "year": year,
            "rating": rate,
            "original_id": article_id,
            "source": "evertime",
            "uploaded_at": datetime.now().isoformat(),
            "text": text  # 리뷰 텍스트도 메타데이터에 포함
        }
        
        # 선택적 필드 추가 (있는 경우만)
        if "department" in course_info:
            metadata["department"] = course_info["department"]
        
        # 리뷰 아이템 생성
        review_item = {
            "id": review_id,
            "text": text,
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
    
    # ==========================================
    # 하드코딩 섹션 - 여기를 수정하세요
    # ==========================================
    
    # 강의 정보 (필수: course_name, professor)
    course_info = {
        "course_name": "기계학습",  # 강의명 (필수)
        "professor": "손경아",      # 교수명 (필수)
        # "department": "소프트웨어학과",  # 학과 (선택사항)
    }
    
    # cURL 명령어 (여기에 실제 cURL 명령어를 입력하세요)
    curl_command = """curl -X GET "https://api.example.com/reviews" -H "Authorization: Bearer YOUR_TOKEN" """
    
    # ==========================================
    
    
    try:
        # cURL 명령어로 API 호출
        print("🌐 API 호출 중...")
        api_response_data = execute_curl_command(curl_command)
        
        # VectorStore 초기화
        print("🔧 VectorStore 초기화 중...")
        vector_store = VectorStore()
        
        # 강의 정보 출력
        print(f"\n📚 강의 정보:")
        print(f"   - 강의명: {course_info['course_name']}")
        print(f"   - 교수명: {course_info['professor']}")
        if "department" in course_info:
            print(f"   - 학과: {course_info['department']}")
        
        # API 응답 데이터 변환
        print("\n🔄 강의평 데이터 변환 중...")
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
