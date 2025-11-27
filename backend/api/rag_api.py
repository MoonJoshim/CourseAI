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
    comparison_targets: Optional[Dict[str, Any]] = None  # 비교 대상 정보
    # comparison_targets 구조:
    # {
    #   "course_names": List[str],  # 비교 대상 강의명 리스트
    #   "professors": List[str],     # 비교 대상 교수명 리스트
    #   "comparison_type": str       # "course" | "professor" | "both" | None
    # }

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
   - 가능한 필드: course_name, professor, department, target_grade, semester, credits, lecture_time, lecture_method, course_type, subject_type
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

4. 비교 대상 추출 (comparison_targets):
   - 질문에서 비교하고 있는 강의명과 교수명을 추출
   - 비교 타입 판단:
     * "course": 여러 강의를 비교하는 경우 (예: "기계학습과 인공지능의 차이")
     * "professor": 한 강의의 여러 교수를 비교하는 경우 (예: "알고리즘 강의 교수님별 차이점")
     * "both": 여러 강의의 여러 교수를 비교하는 경우
     * null: 비교 질의가 아닌 경우
   - course_names: 비교 대상 강의명 리스트 (없으면 빈 배열 [])
   - professors: 비교 대상 교수명 리스트 (없으면 빈 배열 [])
   - 예: "알고리즘 강의 교수님별 차이점 알려줘" → {{"course_names": ["알고리즘"], "professors": [], "comparison_type": "professor"}}
   - 예: "기계학습과 인공지능의 차이가 뭐야?" → {{"course_names": ["기계학습", "인공지능"], "professors": [], "comparison_type": "course"}}
   - 예: "객체지향프로그래밍 어느 교수님이 좋아?" → {{"course_names": ["객체지향프로그래밍"], "professors": [], "comparison_type": "professor"}}
   - 예: "데이터베이스에 대해 배울 수 있는 강의 추천해줘" → {{"course_names": [], "professors": [], "comparison_type": null}}

사용자 질문: "{user_query}"

반드시 다음 JSON 형식으로만 응답하세요 (추가 설명 없이):
{{
    "needs_structured_filter": true/false,
    "filters": {{}},
    "semantic_query": "정제된 질문",
    "comparison_targets": {{
        "course_names": [],
        "professors": [],
        "comparison_type": null
    }}
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
        comparison_targets = intent_data.get("comparison_targets")
        if comparison_targets is None:
            comparison_targets = {
                "course_names": [],
                "professors": [],
                "comparison_type": None
            }
        
        return QueryIntent(
            needs_structured_filter=intent_data.get("needs_structured_filter", False),
            filters=intent_data.get("filters", {}),
            semantic_query=intent_data.get("semantic_query", user_query),
            comparison_targets=comparison_targets
        )
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 파싱 오류: {e}")
        print(f"   Gemini 응답: {response_text if 'response_text' in locals() else 'N/A'}")
        # 파싱 실패 시 기본값 반환
        return QueryIntent(
            needs_structured_filter=False,
            filters={},
            semantic_query=user_query,
            comparison_targets={
                "course_names": [],
                "professors": [],
                "comparison_type": None
            }
        )
    except Exception as e:
        print(f"❌ 질문 의도 분석 오류: {e}")
        import traceback
        traceback.print_exc()
        # 에러 발생 시 기본값 반환
        return QueryIntent(
            needs_structured_filter=False,
            filters={},
            semantic_query=user_query,
            comparison_targets={
                "course_names": [],
                "professors": [],
                "comparison_type": None
            }
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

def semantic_search_pinecone(query: str, candidates: Optional[List[Dict[str, Any]]] = None, top_k: int = 5, comparison_targets: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Pinecone 의미 기반 검색 (metadata 필터 지원, 비교 대상 보장)
    
    Args:
        query: 검색할 쿼리 텍스트
        candidates: MongoDB 후보 목록 (course_name 리스트로 변환하여 필터링에 사용)
        top_k: 반환할 최대 결과 수
        comparison_targets: 비교 대상 정보 (course_names, professors, comparison_type)
    
    Returns:
        List[Dict]: metadata, text를 포함한 검색 결과 리스트
        [
            {
                "text": "문서 내용",
                "metadata": {...}
            },
            ...
        ]
    """
    try:
        # 쿼리 임베딩 생성
        query_embedding = embedding_model.encode([f"query: {query}"], normalize_embeddings=True)[0].tolist()
        
        index = pc.Index(PINECONE_INDEX)
        
        # 비교 대상 보장 검색 결과
        guaranteed_results = []
        guaranteed_keys = set()  # 중복 제거용: (course_name, professor) 튜플
        
        if comparison_targets:
            course_names = comparison_targets.get("course_names", [])
            professors = comparison_targets.get("professors", [])
            comparison_type = comparison_targets.get("comparison_type")
            
            if comparison_type in ["course", "professor", "both"]:
                print(f"🔍 비교 대상 보장 검색: course_names={course_names}, professors={professors}, type={comparison_type}")
                
                # 각 강의명별로 최소 1개씩 검색
                for course_name in course_names:
                    if not course_name:
                        continue
                    
                    course_filter = {"course_name": {"$eq": course_name}}
                    try:
                        course_response = index.query(
                            vector=query_embedding,
                            top_k=1,
                            include_metadata=True,
                            filter=course_filter
                        )
                        
                        for match in course_response.matches:
                            meta = match.metadata
                            key = (meta.get("course_name", ""), meta.get("professor", ""))
                            if key not in guaranteed_keys:
                                guaranteed_results.append({
                                    "text": meta.get("text", ""),
                                    "metadata": meta
                                })
                                guaranteed_keys.add(key)
                    except Exception as e:
                        print(f"⚠️ 강의명 '{course_name}' 검색 오류: {e}")
                
                # 각 교수명별로 최소 1개씩 검색 (교수 비교인 경우)
                if comparison_type in ["professor", "both"]:
                    for professor in professors:
                        if not professor:
                            continue
                        
                        professor_filter = {"professor": {"$eq": professor}}
                        try:
                            professor_response = index.query(
                                vector=query_embedding,
                                top_k=1,
                                include_metadata=True,
                                filter=professor_filter
                            )
                            
                            for match in professor_response.matches:
                                meta = match.metadata
                                key = (meta.get("course_name", ""), meta.get("professor", ""))
                                if key not in guaranteed_keys:
                                    guaranteed_results.append({
                                        "text": meta.get("text", ""),
                                        "metadata": meta
                                    })
                                    guaranteed_keys.add(key)
                        except Exception as e:
                            print(f"⚠️ 교수명 '{professor}' 검색 오류: {e}")
                    
                    # 강의+교수 조합별로 최소 1개씩 검색 (교수 비교인 경우)
                    if course_names and not professors:
                        # course_names는 있지만 professors가 없는 경우, 해당 강의의 모든 교수에 대해 검색
                        for course_name in course_names:
                            if not course_name:
                                continue
                            
                            # 해당 강의의 교수들을 찾기 위해 먼저 검색
                            course_filter = {"course_name": {"$eq": course_name}}
                            try:
                                course_response = index.query(
                                    vector=query_embedding,
                                    top_k=10,  # 여러 교수 찾기 위해 더 많이 가져옴
                                    include_metadata=True,
                                    filter=course_filter
                                )
                                
                                # 교수별로 그룹화하여 각 교수당 최소 1개씩
                                professors_found = {}
                                for match in course_response.matches:
                                    meta = match.metadata
                                    prof_name = meta.get("professor", "")
                                    if prof_name and prof_name not in professors_found:
                                        key = (meta.get("course_name", ""), prof_name)
                                        if key not in guaranteed_keys:
                                            professors_found[prof_name] = {
                                                "text": meta.get("text", ""),
                                                "metadata": meta
                                            }
                                            guaranteed_keys.add(key)
                                
                                for prof_result in professors_found.values():
                                    guaranteed_results.append(prof_result)
                            except Exception as e:
                                print(f"⚠️ 강의 '{course_name}' 교수별 검색 오류: {e}")
        
        # 일반 의미 기반 검색 (보장된 결과와 병합)
        pinecone_filter = {}
        
        if candidates:
            # candidates에서 course_name 리스트 추출
            candidate_course_names = []
            for candidate in candidates:
                course_name = candidate.get("course_name", "")
                if course_name:
                    candidate_course_names.append(course_name)
            
            if candidate_course_names:
                # Pinecone metadata 필터: course_name이 candidates 중 하나와 일치
                pinecone_filter = {
                    "course_name": {"$in": candidate_course_names}
                }
                print(f"🔍 Pinecone 필터 적용: {len(candidate_course_names)}개 course_name")
        
        # 일반 검색 실행 (보장된 결과 제외)
        remaining_k = max(1, top_k - len(guaranteed_results))
        # 비교 대상이 있을 때만 중복 제거를 위해 더 많이 가져옴
        has_comparison = comparison_targets and comparison_targets.get("comparison_type") in ["course", "professor", "both"]
        query_top_k = remaining_k * 2 if has_comparison else remaining_k
        query_kwargs = {
            "vector": query_embedding,
            "top_k": query_top_k,
            "include_metadata": True
        }
        if pinecone_filter:
            query_kwargs["filter"] = pinecone_filter
        
        query_response = index.query(**query_kwargs)
        
        # 일반 검색 결과 추가 (중복 제거)
        semantic_results = []
        for match in query_response.matches:
            meta = match.metadata
            key = (meta.get("course_name", ""), meta.get("professor", ""))
            if key not in guaranteed_keys:
                semantic_results.append({
                    "text": meta.get("text", ""),
                    "metadata": meta
                })
                guaranteed_keys.add(key)
        
        # 보장된 결과 + 일반 검색 결과 병합 (최대 top_k개)
        all_results = guaranteed_results + semantic_results
        final_results = all_results[:top_k]
        
        print(f"✅ Pinecone에서 {len(final_results)}개 강의평 발견 (보장: {len(guaranteed_results)}, 일반: {len(semantic_results)})")
        return final_results
        
    except Exception as e:
        print(f"❌ Pinecone 검색 오류: {e}")
        import traceback
        traceback.print_exc()
        return []

def merge_results(mongo_candidates: Optional[List[Dict[str, Any]]], pinecone_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    두 결과를 merge → 강의 정보 + 리뷰 정보 통합
    
    Args:
        mongo_candidates: MongoDB에서 검색된 강의 정보 리스트
        pinecone_results: Pinecone에서 검색된 강의평 리스트
        
    Returns:
        Dict: 병합된 강의 정보 (course_name별로 그룹화, 리뷰 포함)
    """
    # course_name별로 강의평 그룹화
    reviews_by_course = defaultdict(list)
    
    for review in pinecone_results:
        metadata = review.get("metadata", {})
        course_name = metadata.get("course_name", "")
        
        if course_name:
            review_data = {
                "text": review.get("text", ""),
                "review_id": metadata.get("original_id", ""),
                "sentiment": None  # 향후 감정 분석 추가 가능
            }
            reviews_by_course[course_name].append(review_data)
    
    # MongoDB 강의 정보가 있는 경우
    if mongo_candidates:
        courses = []
        mongo_course_map = {course.get("course_name", ""): course for course in mongo_candidates if course.get("course_name")}
        
        for course_name, reviews in reviews_by_course.items():
            mongo_course = mongo_course_map.get(course_name, {})
            
            course_entry = {
                "course_name": course_name,
                "professor": mongo_course.get("professor", ""),
                "department": mongo_course.get("department", ""),
                "rating": mongo_course.get("rating", 0.0) or mongo_course.get("average_rating", 0.0),
                "review_count": len(reviews),
                "reviews": reviews
            }
            courses.append(course_entry)
        
        # MongoDB에 있지만 리뷰가 없는 강의도 추가
        for course in mongo_candidates:
            course_name = course.get("course_name", "")
            if course_name and course_name not in reviews_by_course:
                course_entry = {
                    "course_name": course_name,
                    "professor": course.get("professor", ""),
                    "department": course.get("department", ""),
                    "rating": course.get("rating", 0.0) or course.get("average_rating", 0.0),
                    "review_count": 0,
                    "reviews": []
                }
                courses.append(course_entry)
    else:
        # MongoDB 후보가 없는 경우 (semantic-only queries)
        # Pinecone metadata에서만 강의 정보 추출
        courses = []
        course_info_map = {}
        
        for review in pinecone_results:
            metadata = review.get("metadata", {})
            course_name = metadata.get("course_name", "")
            
            if course_name and course_name not in course_info_map:
                course_info_map[course_name] = {
                    "professor": metadata.get("professor", ""),
                    "department": metadata.get("department", ""),
                    "rating": metadata.get("rating", 0.0)
                }
        
        for course_name, reviews in reviews_by_course.items():
            info = course_info_map.get(course_name, {})
            course_entry = {
                "course_name": course_name,
                "professor": info.get("professor", ""),
                "department": info.get("department", ""),
                "rating": float(info.get("rating", 0.0)) if info.get("rating") else 0.0,
                "review_count": len(reviews),
                "reviews": reviews
            }
            courses.append(course_entry)
    
    return {
        "courses": courses
    }

def normalize_context(merged_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    병합된 컨텍스트를 정규화하여 LLM 프롬프트에 안전하게 사용할 수 있도록 처리
    
    Args:
        merged_context: merge_results()의 출력
        
    Returns:
        Dict: 정규화된 컨텍스트 (모든 필수 필드 보장, 리뷰 텍스트 길이 제한)
    """
    normalized = {
        "courses": []
    }
    
    for course in merged_context.get("courses", []):
        # 필수 필드 보장
        normalized_course = {
            "course_name": course.get("course_name", ""),
            "professor": course.get("professor", ""),
            "department": course.get("department", ""),
            "rating": float(course.get("rating", 0.0)),
            "review_count": int(course.get("review_count", 0)),
            "reviews": []
        }
        
        # 리뷰 정규화 (텍스트 길이 제한)
        reviews = course.get("reviews", [])
        for review in reviews:
            review_text = review.get("text", "")
            # 리뷰 텍스트가 너무 길면 첫 200자만 사용
            if len(review_text) > 200:
                review_text = review_text[:200] + "..."
            
            normalized_review = {
                "text": review_text,
                "review_id": review.get("review_id", ""),
                "sentiment": review.get("sentiment")
            }
            normalized_course["reviews"].append(normalized_review)
        
        # review_count를 실제 리뷰 개수로 업데이트
        normalized_course["review_count"] = len(normalized_course["reviews"])
        
        normalized["courses"].append(normalized_course)
    
    return normalized

def synthesize_answer_with_llm(user_query: str, merged_context: Dict[str, Any], conversation_history: list = None) -> str:
    """
    LLM 최종 응답 생성 (Gemini)
    
    Args:
        user_query: 사용자 질문
        merged_context: merge_results()의 출력
        conversation_history: 대화 히스토리 (선택적)
        
    Returns:
        str: Gemini가 생성한 최종 답변
    """
    try:
        # 컨텍스트 정규화
        normalized_context = normalize_context(merged_context)
        
        # 대화 히스토리 텍스트 생성 (최근 5개만)
        history_text = ""
        if conversation_history:
            history_items = []
            for hist in conversation_history[-5:]:
                user_msg = hist.get("user", "").strip()
                assistant_msg = hist.get("assistant", "").strip()
                if user_msg and assistant_msg:
                    history_items.append(f"사용자: {user_msg}\n어시스턴트: {assistant_msg}")
            if history_items:
                history_text = "\n\n이전 대화(있으면):\n" + "\n\n".join(history_items) + "\n"
        
        # 프롬프트 구성
        prompt = f"""{history_text}사용자 질문:
{user_query}

아래는 데이터베이스에서 검색된 강의 정보 및 강의평 리뷰 데이터입니다.
이 정보를 기반으로 사용자에게 적절한 답변을 생성하세요.

요구사항:
1) 사용자의 질문 의도에 맞는 추천 또는 조언 제시가 가장 중요합니다.
2) 필요한 경우 강의 특징 요약 또는 교수님의 강의 스타일/특징 요약
4) 필요한 경우 강의평을 기반으로 장점/단점 정리
5) 여러 강의가 있을 경우 정확도 높은 순서대로 최대 3개까지 비교 후 안내
6) 정보가 존재하지 않으면 절대 거짓 생성하지 말고, 사실대로 존재하지 않는다고 말할 것
7) JSON이 아니라 자연스러운 한국어 문장으로 답변 생성
8) 강의평에 과도하게 비난적인 내용이나 부정적인 내용은 배제하거나 순화해서 말할 것
9) 필요시 간단한 포맷팅을 사용할 수 있습니다:
   - 강조가 필요한 부분은 **굵게** 표시
   - 기울임이 필요한 부분은 *기울임* 표시
   - 여러 항목 나열 시 줄바꿈 활용
   - 단, 과도한 포맷팅은 피하고 자연스러운 문장을 유지하세요

강의 데이터(JSON):
{json.dumps(normalized_context, ensure_ascii=False, indent=2)}"""

        # Gemini 모델 호출
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        # 응답 안전하게 처리 (ai_api.py의 generate_gemini_response와 동일한 방식)
        # getattr로 안전하게 접근하고, 실패 시 str(response)로 fallback
        response_text = getattr(response, 'text', None) or str(response)
        
        # 빈 응답이거나 에러 메시지인 경우 처리
        if not response_text or len(response_text.strip()) == 0:
            # candidates에서 직접 추출 시도
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                finish_reason = getattr(candidate, 'finish_reason', None)
                
                # finish_reason 확인 (1=STOP 정상, 2=MAX_TOKENS, 3=SAFETY, 4=RECITATION)
                if finish_reason == 3:  # SAFETY - 안전 필터에 걸림
                    return "죄송합니다. 안전 필터로 인해 답변을 생성할 수 없습니다. 다른 질문을 시도해주세요."
                elif finish_reason == 2:  # MAX_TOKENS - 토큰 제한
                    return "답변이 너무 길어서 일부가 잘렸습니다."
                elif finish_reason == 4:  # RECITATION - 인용 문제
                    return "인용 문제로 인해 답변을 생성할 수 없습니다."
                
                # parts에서 텍스트 추출
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        parts_text = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                parts_text.append(part.text)
                        if parts_text:
                            return '\n'.join(parts_text)
            
            return "답변을 생성할 수 없습니다. 다시 시도해주세요."
        
        return response_text
        
    except Exception as e:
        print(f"❌ LLM 답변 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        return f"답변 생성 중 오류가 발생했습니다: {str(e)}"

# ───────────────────────────────────────────────
# RAG Chat API 엔드포인트
# ───────────────────────────────────────────────
# 
# 요청 예시:
# POST /api/v2/rag/chat
# Content-Type: application/json
# {
#   "query": "데이터베이스 강의 추천해줘",
#   "history": [
#     {
#       "user": "알고리즘 강의 추천해줘",
#       "assistant": "알고리즘 강의로는..."
#     }
#   ]
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
        conversation_history = body.get("history", [])  # 대화 히스토리 (선택적)
        
        if not user_query:
            return jsonify({"error": "query 파라미터가 필요합니다."}), 400
        
        # Step 1: 질문 분석 (Structured / Semantic 분리)
        intent = classify_query_intent(user_query)
        
        # Step 2: 구조적 필터 필요 여부 확인
        if intent.needs_structured_filter:
            mongo_candidates = filter_from_mongodb(intent.filters)
        else:
            mongo_candidates = None
        
        # Step 3: Pinecone 의미 기반 검색 (비교 대상 보장)
        comparison_targets = intent.comparison_targets
        pinecone_results = semantic_search_pinecone(
            query=intent.semantic_query,
            candidates=mongo_candidates,
            comparison_targets=comparison_targets
        )
        
        # Step 4: 두 결과를 merge → 강의 정보 + 리뷰 정보 통합
        merged_context = merge_results(
            mongo_candidates,
            pinecone_results
        )
        
        # Step 5: Pinecone 결과를 top_reviews 형식으로 변환
        top_reviews = []
        for result in pinecone_results[:5]:  # 상위 5개만
            metadata = result.get("metadata", {})
            review_text = result.get("text", "")  # 강의평 텍스트
            review_rating = metadata.get("rating", None)
            
            # rating이 숫자면 float로 변환, 아니면 None
            if review_rating is not None:
                try:
                    review_rating = float(review_rating)
                except (ValueError, TypeError):
                    review_rating = None
            
            review_item = {
                "course_name": metadata.get("course_name", ""),
                "professor": metadata.get("professor", ""),
                "text": review_text,  # 강의평 텍스트
                "rating": review_rating,  # 강의평의 rating
            }
            top_reviews.append(review_item)
        
        # Step 6: LLM 최종 응답 생성 (Gemini)
        final_answer = synthesize_answer_with_llm(
            user_query,
            merged_context,
            conversation_history
        )
        
        # Step 7: 응답 반환
        return jsonify({
            "answer": final_answer,
            "top_reviews": top_reviews,
            "provider": "rag-v2",
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