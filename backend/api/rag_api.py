#!/usr/bin/env python3
"""Pinecone 강의 데이터 API"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from langchain_pinecone import PineconeVectorStore
from typing import List, Dict, Any, Optional
import google.generativeai as genai

# LangChain Embeddings import (버전에 따라 경로가 다를 수 있음)
try:
    from langchain_core.embeddings import Embeddings
except ImportError:
    try:
        from langchain.embeddings.base import Embeddings
    except ImportError:
        from langchain.embeddings import Embeddings

# ───────────────────────────────────────────────
# 기본 설정
# ───────────────────────────────────────────────
load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

# ───────────────────────────────────────────────
# Pinecone 연결
# ───────────────────────────────────────────────
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX = os.getenv('PINECONE_INDEX', 'courses-dev')

pc = Pinecone(api_key=PINECONE_API_KEY)

# ───────────────────────────────────────────────
# Embedding 모델 - multilingual-e5-base
# ───────────────────────────────────────────────
# embedding_model = SentenceTransformer("intfloat/multilingual-e5-base")
embedding_model = SentenceTransformer("jhgan/ko-sroberta-multitask")

# ───────────────────────────────────────────────
# LangChain Embeddings 인터페이스 구현
# ───────────────────────────────────────────────
class SentenceTransformerEmbeddings(Embeddings):
    """SentenceTransformer를 LangChain Embeddings 인터페이스로 래핑"""
    
    def __init__(self, model: SentenceTransformer):
        self.model = model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """문서 임베딩 (passage 프리픽스 사용)"""
        # E5 모델은 passage 프리픽스 사용
        formatted = [f"passage: {text}" for text in texts]
        embeddings = self.model.encode(formatted, normalize_embeddings=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """쿼리 임베딩 (query 프리픽스 사용)"""
        # E5 모델은 query 프리픽스 사용
        formatted = f"query: {text}"
        embedding = self.model.encode([formatted], normalize_embeddings=True)
        return embedding[0].tolist()

# ───────────────────────────────────────────────
# VectorStore 초기화 함수
# ───────────────────────────────────────────────
def init_vectorstore() -> PineconeVectorStore:
    """
    Pinecone VectorStore 초기화
    upsert와 동일한 구조로 생성
    """
    embeddings = SentenceTransformerEmbeddings(embedding_model)
    vectorstore = PineconeVectorStore(
        index_name=PINECONE_INDEX,
        embedding=embeddings
    )
    return vectorstore

# ───────────────────────────────────────────────
# LangChain Pinecone VectorStore (전역 인스턴스)
# ───────────────────────────────────────────────
vectorstore = init_vectorstore()

# ───────────────────────────────────────────────
# Gemini LLM 호출
# ───────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def call_gemini(prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

# ───────────────────────────────────────────────
# Intent 클래스 (질문 의도 분석 결과)
# ───────────────────────────────────────────────
class QueryIntent:
    """질문 의도 분석 결과"""
    def __init__(self, needs_structured_filter: bool = False, filters: Optional[Dict[str, Any]] = None, semantic_query: str = ""):
        self.needs_structured_filter = needs_structured_filter
        self.filters = filters or {}
        self.semantic_query = semantic_query

# ───────────────────────────────────────────────
# Helper 함수들 (Stub 구현)
# ───────────────────────────────────────────────
def classify_query_intent(user_query: str) -> QueryIntent:
    """질문 의도 분석 (Structured / Semantic 분리)"""
    # TODO: 구현 필요
    return QueryIntent(
        needs_structured_filter=False,
        filters={},
        semantic_query=user_query
    )

def filter_from_mongodb(filters: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """MongoDB에서 구조적 필터로 강의 검색"""
    # TODO: 구현 필요
    return None

def semantic_search_pinecone(query: str, candidates: Optional[List[Dict[str, Any]]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Pinecone 의미 기반 검색
    
    Args:
        query: 검색할 쿼리 텍스트
        candidates: MongoDB 후보 목록 (현재 미사용, 향후 필터링에 사용 예정)
        top_k: 반환할 최대 결과 수
        
    Returns:
        List[Dict]: metadata와 text를 포함한 검색 결과 리스트
        [
            {
                "text": "문서 내용",
                "metadata": {...}
            },
            ...
        ]
    """
    try:
        # VectorStore에서 retriever 생성
        retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
        
        # 검색 실행 (embed_query가 자동으로 "query:" 프리픽스 추가)
        # Note: embed_query 메서드가 이미 "query: {text}" 형식으로 처리하므로
        # 원본 query를 그대로 전달하면 됨
        docs = retriever.get_relevant_documents(query)
        
        # 결과를 Dict 형태로 변환
        results = []
        for doc in docs:
            results.append({
                "text": doc.page_content,
                "metadata": doc.metadata
            })
        
        # TODO: candidates를 사용한 필터링 로직 추가 예정 (MongoDB 통합 시)
        
        return results
        
    except Exception as e:
        print(f"❌ Pinecone 검색 오류: {e}")
        import traceback
        traceback.print_exc()
        return []

def merge_results(mongo_candidates: Optional[List[Dict[str, Any]]], pinecone_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """두 결과를 merge → 강의 정보 + 리뷰 정보 통합"""
    # TODO: 구현 필요
    return {
        "courses": mongo_candidates or [],
        "reviews": pinecone_results
    }

def synthesize_answer_with_llm(user_query: str, merged_context: Dict[str, Any]) -> str:
    """LLM 최종 응답 생성 (Gemini)"""
    # TODO: 구현 필요
    return "답변 생성 중..."

# ───────────────────────────────────────────────
# RAG Chat API 엔드포인트
# ───────────────────────────────────────────────
# 
# 요청 예시:
# POST /api/v2/rag/chat
# Content-Type: application/json
# {
#   "query": "데이터베이스 강의 추천해줘"
# }
#
# 응답 예시 (성공):
# {
#   "answer": "답변 생성 중...",
#   "debug": {
#     "intent": {
#       "needs_structured_filter": false,
#       "filters": {},
#       "semantic_query": "데이터베이스 강의 추천해줘"
#     },
#     "mongo_candidates": 0,
#     "pinecone_hits": 0
#   }
# }
@app.route("/api/v2/rag/chat", methods=["POST"])
def rag_chat():
    """RAG 기반 챗봇 API"""
    try:
        body = request.get_json()
        user_query = body.get("query", "").strip()
        
        if not user_query:
            return jsonify({"error": "query 파라미터가 필요합니다."}), 400
        
        # Step 1: 질문 분석 (Structured / Semantic 분리)
        intent = classify_query_intent(user_query)
        
        # Step 2: 구조적 필터 필요 여부 확인
        if intent.needs_structured_filter:
            mongo_candidates = filter_from_mongodb(intent.filters)
        else:
            mongo_candidates = None
        
        # Step 3: Pinecone 의미 기반 검색
        pinecone_results = semantic_search_pinecone(
            query=intent.semantic_query,
            candidates=mongo_candidates
        )
        
        # Step 4: 두 결과를 merge → 강의 정보 + 리뷰 정보 통합
        merged_context = merge_results(
            mongo_candidates,
            pinecone_results
        )
        
        # Step 5: LLM 최종 응답 생성 (Gemini)
        final_answer = synthesize_answer_with_llm(
            user_query,
            merged_context
        )
        
        # Step 6: 응답 반환
        return jsonify({
            "answer": final_answer,
            "debug": {
                "intent": {
                    "needs_structured_filter": intent.needs_structured_filter,
                    "filters": intent.filters,
                    "semantic_query": intent.semantic_query
                },
                "mongo_candidates": len(mongo_candidates) if mongo_candidates else 0,
                "pinecone_hits": len(pinecone_results)
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)