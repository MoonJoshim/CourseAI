"""
Pinecone 벡터 스토어 모델
강의평 데이터의 벡터화 및 저장/검색 기능
"""

import os
from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import hashlib

# 환경변수 로드
load_dotenv()

class VectorStore:
    """Pinecone 벡터 스토어 관리 클래스"""
    
    def __init__(self):
        """Pinecone 클라이언트 초기화"""
        self.pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        self.index_name = os.environ.get("PINECONE_INDEX", "courses-reviews")
        self.index = self.pc.Index(self.index_name)
        
        # 임베딩 모델 초기화
        model_name = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.embedder = SentenceTransformer(model_name)
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
            vectors = self.embed_texts(texts)
            
            # Pinecone 업서트 형식으로 변환
            upsert_vectors = []
            for idx, (item, vector) in enumerate(zip(review_items, vectors)):
                # ✅ 항상 ASCII-safe ID 사용
                original_id = item.get("id", "")
                safe_id = f"review_{hashlib.md5(original_id.encode('utf-8')).hexdigest()[:10]}_{idx:03d}"

                metadata = item["metadata"]
                metadata["original_id"] = original_id  # 한글 ID 보존
                upsert_vectors.append({
                    "id": safe_id,
                    "values": vector,
                    "metadata": metadata
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
