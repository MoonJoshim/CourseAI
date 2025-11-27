#!/usr/bin/env python3
"""Pinecone 강의 데이터 API"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import sys
from dotenv import load_dotenv
from pinecone import Pinecone
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from langchain_pinecone import PineconeVectorStore
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import google.generativeai as genai

# 프로젝트 루트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.api import get_mongo_db

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
class QueryIntent(BaseModel):
    """질문 의도 분석 결과"""
    needs_structured_filter: bool
    filters: Dict[str, Any]
    semantic_query: str

# ───────────────────────────────────────────────
# Helper 함수들
# ───────────────────────────────────────────────
def classify_query_intent(user_query: str) -> QueryIntent:
    """
    질문 의도 분석 (Structured / Semantic 분리)
    Gemini를 사용하여 사용자 질문을 분석하고 구조적 필터와 의미 검색 쿼리를 분리
    
    Args:
        user_query: 사용자 질문
        
    Returns:
        QueryIntent: 분석된 의도 정보
    """
    try:
        # Gemini 프롬프트 구성
        prompt = f"""사용자 질문을 분석하여 다음 정보를 JSON 형식으로 반환해주세요:

1. 구조적 필터 필요 여부 (needs_structured_filter):
   - MongoDB course에 있는 필드로 필터링이 필요한지 판단
   - 예: "소프트웨어학과 전공 필수(전필) 과목 추천해줘" → true (department, course_type 필터 필요)
   - 예: "데이터베이스 들을까 말까?" → true (course_name 필터 필요)
   - 예: "이번 학기에 열리는 쉬운 전공 선택(전선) 과목 중에 비대면 강의 추천해줘" → true (semester, lecture_type, course_type 필터 필요)
   - 예: "손경아 교수님 어때?" → true (professor 필터 필요)
   - 예: "과제 별로 없는 강의 추천해줘" → false (구조적 필터 불필요)
   - 예: "내 개발 실력에 진짜 도움되는 강의 있을까?" → false (구조적 필터 불필요)

2. MongoDB 필터 (filters):
   - 구조적 필터가 필요한 경우, 추출 가능한 필드들을 key-value 형태로 제공
   - 가능한 필드: course_name, professor, department, semester, credits, lecture_time, lecture_method, course_type, subject_type
   - department는 "소프트웨어학과"밖에 올 수 없고, course_type는 "전필", "전선"밖에 올 수 없음. lecture_time는 "월", "화", "수", "목", "금"밖에 올 수 없음.
   - 예: {{"course_name": "데이터베이스"}}, {{"department": "소프트웨어학과", "course_type": "전선"}}
   - 구조적 필터가 불필요하면 빈 객체 {{}} 반환

3. 의미 검색 쿼리 (semantic_query):
   - 구조적 필터 부분을 제외한 나머지 자연어 질문을 정제
   - 구조적 필터가 필요한 경우: 필터에 해당하는 부분(과목명, 교수명, 학과명, 학기, 수업방식 등)을 제거하고 나머지 의미 있는 질문만 남김
   - 구조적 필터가 불필요한 경우: 원본 질문 그대로 사용
   - 중요: semantic_query가 너무 짧거나 의미가 불명확한 경우(예: "들을까 말까?"), 강의평이나 강의 정보를 검색할 수 있도록 의미를 확장하거나, 장단점을 확인할 수 있도록 검색 및 정리 수행
   - 예: "소프트웨어학과 전공 필수(전필) 과목 추천해줘" → "과목 추천해줘" (department, course_type 제거)
   - 예: "SW캡스톤디자인 들을까 말까?" → "강의 어때" 또는 "강의 장단점 정리해줘" (course_name 제거, 의미 확장)
   - 예: "이번 학기에 열리는 데이터베이스 강의 추천해줘" → "강의 추천해줘" (course_name, semester 제거)
   - 예: "이번 학기에 열리는 쉬운 전공 선택(전선) 과목 중에 비대면 강의 추천해줘" → "쉬운 강의 추천해줘" (semester, lecture_type, course_type 제거)
   - 예: "손경아 교수님 어때?" → "교수님 강의 어때" (professor 제거, 의미 확장)
   - 예: "과제 별로 없는 강의 추천해줘" → "과제 별로 없는 강의 추천해줘" (구조적 필터 없음, 원본 그대로)
   - 예: "내 개발 실력에 진짜 도움되는 강의 있을까?" → "내 개발 실력에 진짜 도움되는 강의 있을까?" (구조적 필터 없음, 원본 그대로)

사용자 질문: "{user_query}"

반드시 다음 JSON 형식으로만 응답하세요 (추가 설명 없이):
{{
    "needs_structured_filter": true/false,
    "filters": {{}},
    "semantic_query": "정제된 질문"
}}"""

        # Gemini 모델 호출
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # JSON 파싱 (마크다운 코드 블록 제거)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # JSON 파싱
        intent_data = json.loads(response_text)
        
        # QueryIntent 객체 생성
        return QueryIntent(
            needs_structured_filter=intent_data.get("needs_structured_filter", False),
            filters=intent_data.get("filters", {}),
            semantic_query=intent_data.get("semantic_query", user_query)
        )
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 파싱 오류: {e}")
        print(f"   Gemini 응답: {response_text if 'response_text' in locals() else 'N/A'}")
        # 파싱 실패 시 기본값 반환
        return QueryIntent(
            needs_structured_filter=False,
            filters={},
            semantic_query=user_query
        )
    except Exception as e:
        print(f"❌ 질문 의도 분석 오류: {e}")
        import traceback
        traceback.print_exc()
        # 에러 발생 시 기본값 반환
        return QueryIntent(
            needs_structured_filter=False,
            filters={},
            semantic_query=user_query
        )

def filter_from_mongodb(filters: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """
    MongoDB에서 구조적 필터로 강의 검색
    
    Args:
        filters: 필터 딕셔너리 (department, course_name, professor, 
                semester, credits, course_type, subject_type, lecture_time, lecture_method 등)
        
    Returns:
        List[Dict]: 강의 정보 리스트 (course_name, professor, department 등 포함)
    """
    try:
        if not filters:
            return None
        
        db = get_mongo_db()
        collection = db.courses
        
        # 동적 쿼리 구성
        query = {}
        
        # department 필터
        if "department" in filters:
            query["department"] = {"$regex": filters["department"], "$options": "i"}
        
        # course_name 필터
        if "course_name" in filters:
            query["course_name"] = {"$regex": filters["course_name"], "$options": "i"}
        
        # professor 필터
        if "professor" in filters:
            query["professor"] = {"$regex": filters["professor"], "$options": "i"}
        
        # semester 필터 (year와 별도)
        if "semester" in filters:
            query["semester"] = filters["semester"]
        
        # credits 필터
        if "credits" in filters:
            query["credits"] = filters["credits"]
        
        # course_type 필터 (전필, 전선 등)
        if "course_type" in filters:
            query["course_type"] = {"$regex": filters["course_type"], "$options": "i"}
        
        # subject_type 필터
        if "subject_type" in filters:
            query["subject_type"] = {"$regex": filters["subject_type"], "$options": "i"}
        
        # lecture_time 필터
        if "lecture_time" in filters:
            query["lecture_time"] = {"$regex": filters["lecture_time"], "$options": "i"}
        
        # lecture_method 필터 (비대면, 대면 등)
        if "lecture_method" in filters:
            query["lecture_method"] = {"$regex": filters["lecture_method"], "$options": "i"}
        
        if not query:
            return None
        
        # MongoDB 검색 실행
        cursor = collection.find(query).limit(100)  # 최대 100개
        results = []
        
        for doc in cursor:
            course_data = {
                "course_name": doc.get("course_name", ""),
                "professor": doc.get("professor", ""),
                "department": doc.get("department", ""),
                "semester": doc.get("semester", ""),
                "credits": doc.get("credits", 3),
                "course_type": doc.get("course_type", ""),
                "subject_type": doc.get("subject_type", ""),
                "lecture_time": doc.get("lecture_time", ""),
                "lecture_method": doc.get("lecture_method", ""),
                "course_id": doc.get("course_id", ""),
                "rating": doc.get("rating", 0.0),
                "average_rating": doc.get("average_rating", 0.0),
                "total_reviews": doc.get("total_reviews", 0)
            }
            results.append(course_data)
        
        print(f"✅ MongoDB에서 {len(results)}개 강의 발견 (필터: {filters})")
        return results if results else None
        
    except Exception as e:
        print(f"❌ MongoDB 필터링 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

def semantic_search_pinecone(query: str, candidates: Optional[List[Dict[str, Any]]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Pinecone 의미 기반 검색 (metadata 필터 지원)
    
    Args:
        query: 검색할 쿼리 텍스트
        candidates: MongoDB 후보 목록 (course_name 리스트로 변환하여 필터링에 사용)
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
        # Pinecone 필터 구성
        pinecone_filter = {}
        
        if candidates:
            # candidates에서 course_name 리스트 추출
            course_names = []
            for candidate in candidates:
                course_name = candidate.get("course_name", "")
                if course_name:
                    course_names.append(course_name)
            
            if course_names:
                # Pinecone metadata 필터: course_name이 candidates 중 하나와 일치
                pinecone_filter = {
                    "course_name": {"$in": course_names}
                }
                print(f"🔍 Pinecone 필터 적용: {len(course_names)}개 course_name")
        
        # VectorStore에서 retriever 생성 (필터 포함)
        search_kwargs = {"k": top_k}
        if pinecone_filter:
            search_kwargs["filter"] = pinecone_filter
        
        retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
        
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
        
        print(f"✅ Pinecone에서 {len(results)}개 강의평 발견")
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
                "intent": intent.model_dump(),  # Pydantic BaseModel을 dict로 변환
                "mongo_candidates": len(mongo_candidates) if mongo_candidates else 0,
                "pinecone_hits": len(pinecone_results)
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ───────────────────────────────────────────────
# 테스트 엔드포인트
# ───────────────────────────────────────────────
@app.route("/api/v2/rag/test/intent", methods=["POST"])
def test_classify_intent():
    """
    질문 의도 분석 테스트 엔드포인트
    
    요청 예시:
    POST /api/v2/rag/test/intent
    Content-Type: application/json
    {
      "query": "소프트웨어학과 전공 필수(전필) 과목 추천해줘"
    }
    
    응답 예시:
    {
      "query": "소프트웨어학과 전공 필수(전필) 과목 추천해줘",
      "intent": {
        "needs_structured_filter": true,
        "filters": {
          "department": "소프트웨어학과",
          "course_type": "전필"
        },
        "semantic_query": "과목 추천해줘"
      }
    }
    """
    try:
        body = request.get_json() or {}
        user_query = body.get("query", "").strip()
        
        if not user_query:
            return jsonify({"error": "query 파라미터가 필요합니다."}), 400
        
        # 질문 의도 분석
        intent = classify_query_intent(user_query)
        
        return jsonify({
            "query": user_query,
            "intent": intent.model_dump()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v2/rag/test/intent/batch", methods=["POST"])
def test_classify_intent_batch():
    """
    여러 질문을 한번에 테스트하는 엔드포인트
    
    요청 예시:
    POST /api/v2/rag/test/intent/batch
    Content-Type: application/json
    {
      "queries": [
        "소프트웨어학과 전공 필수(전필) 과목 추천해줘",
        "이번 학기에 열리는 데이터베이스 강의 추천해줘",
        "손경아 교수님 어때?",
        "과제 별로 없는 강의 추천해줘"
      ]
    }
    """
    try:
        body = request.get_json() or {}
        queries = body.get("queries", [])
        
        if not queries or not isinstance(queries, list):
            return jsonify({"error": "queries 파라미터가 필요합니다. (배열)"}), 400
        
        results = []
        for query in queries:
            try:
                intent = classify_query_intent(query)
                results.append({
                    "query": query,
                    "intent": intent.model_dump(),
                    "success": True
                })
            except Exception as e:
                results.append({
                    "query": query,
                    "error": str(e),
                    "success": False
                })
        
        return jsonify({
            "total": len(queries),
            "results": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v2/rag/test/mongodb", methods=["POST"])
def test_mongodb_filter():
    """
    MongoDB 필터링 테스트 엔드포인트 (질문으로 자동 분석)
    
    요청 예시:
    POST /api/v2/rag/test/mongodb
    Content-Type: application/json
    {
      "query": "소프트웨어학과 전공 필수(전필) 과목 추천해줘"
    }
    """
    try:
        body = request.get_json() or {}
        user_query = body.get("query", "").strip()
        
        if not user_query:
            return jsonify({"error": "query 파라미터가 필요합니다."}), 400
        
        # Intent 분석 후 filters 추출
        intent = classify_query_intent(user_query)
        filters = intent.filters
        
        # 구조적 필터가 불필요한 경우
        if not intent.needs_structured_filter or not filters:
            return jsonify({
                "query": user_query,
                "intent": intent.model_dump(),
                "message": "구조적 필터가 불필요한 질문입니다. MongoDB 필터링을 건너뜁니다.",
                "filters": {},
                "count": 0,
                "results": []
            })
        
        # MongoDB 필터링 실행
        results = filter_from_mongodb(filters)
        
        return jsonify({
            "query": user_query,
            "intent": intent.model_dump(),
            "filters": filters,
            "count": len(results) if results else 0,
            "results": results or []
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v2/rag/test/pinecone", methods=["POST"])
def test_pinecone_search():
    """
    Pinecone 검색 테스트 엔드포인트
    
    요청 예시:
    POST /api/v2/rag/test/pinecone
    Content-Type: application/json
    {
      "query": "과제 별로 없는 강의",
      "candidates": [
        {"course_name": "데이터베이스"},
        {"course_name": "자료구조"}
      ],
      "top_k": 5
    }
    """
    try:
        body = request.get_json() or {}
        query = body.get("query", "").strip()
        candidates = body.get("candidates", None)
        top_k = body.get("top_k", 5)
        
        if not query:
            return jsonify({"error": "query 파라미터가 필요합니다."}), 400
        
        # Pinecone 검색 실행
        results = semantic_search_pinecone(query, candidates, top_k)
        
        return jsonify({
            "query": query,
            "candidates_count": len(candidates) if candidates else 0,
            "top_k": top_k,
            "results_count": len(results),
            "results": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v2/rag/test/full", methods=["POST"])
def test_full_rag_pipeline():
    """
    전체 RAG 파이프라인 테스트 엔드포인트 (답변 생성 제외)
    
    요청 예시:
    POST /api/v2/rag/test/full
    Content-Type: application/json
    {
      "query": "소프트웨어학과 전공 필수(전필) 과목 추천해줘"
    }
    """
    try:
        body = request.get_json() or {}
        user_query = body.get("query", "").strip()
        
        if not user_query:
            return jsonify({"error": "query 파라미터가 필요합니다."}), 400
        
        # Step 1: 질문 분석
        intent = classify_query_intent(user_query)
        
        # Step 2: MongoDB 필터링
        mongo_candidates = None
        if intent.needs_structured_filter:
            mongo_candidates = filter_from_mongodb(intent.filters)
        
        # Step 3: Pinecone 검색
        pinecone_results = semantic_search_pinecone(
            query=intent.semantic_query,
            candidates=mongo_candidates
        )
        
        # Step 4: 결과 병합
        merged_context = merge_results(mongo_candidates, pinecone_results)
        
        return jsonify({
            "query": user_query,
            "intent": intent.model_dump(),
            "mongo_candidates": {
                "count": len(mongo_candidates) if mongo_candidates else 0,
                "courses": mongo_candidates[:5] if mongo_candidates else []  # 최대 5개만 표시
            },
            "pinecone_results": {
                "count": len(pinecone_results),
                "reviews": pinecone_results[:5]  # 최대 5개만 표시
            },
            "merged_context": merged_context
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)