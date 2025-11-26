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
from typing import List
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
# LangChain Pinecone VectorStore
# ───────────────────────────────────────────────
embeddings = SentenceTransformerEmbeddings(embedding_model)

vectorstore = PineconeVectorStore(
    index_name=PINECONE_INDEX,
    embedding=embeddings  # Embeddings 클래스 인스턴스
)

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
# TEST 1: Pinecone index 목록 확인 API
# ───────────────────────────────────────────────
@app.route("/api/test/pinecone", methods=["GET"])
def test_pinecone():
    try:
        indexes = pc.list_indexes()
        return jsonify({"indexes": [idx.name for idx in indexes]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ───────────────────────────────────────────────
# TEST 2: 벡터 저장 테스트
# ───────────────────────────────────────────────
@app.route("/api/test/upsert", methods=["POST"])
def upsert_test():
    body = request.get_json()
    text = body.get("text", "")
    course_id = body.get("course_id", "TEST101")

    try:
        vectorstore.add_texts(
            texts=[text],
            metadatas=[{"course_id": course_id}],
            ids=[f"{course_id}-001"]
        )
        return jsonify({"status": "ok", "message": "Upsert 성공"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ───────────────────────────────────────────────
# TEST 3: 벡터 검색 테스트
# ───────────────────────────────────────────────
@app.route("/api/test/search", methods=["POST"])
def search_test():
    body = request.get_json()
    query = body.get("query", "")
    k = body.get("k", 3)

    try:
        # similarity_search_with_score를 사용하여 유사도 점수도 함께 반환
        docs_with_scores = vectorstore.similarity_search_with_score(query, k=k)
        return jsonify({
            "query": query,
            "results": [
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)  # 유사도 점수 추가
                }
                for doc, score in docs_with_scores
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ───────────────────────────────────────────────
# TEST 4: Gemini 호출 테스트
# ───────────────────────────────────────────────
@app.route("/api/test/gemini")
def test_gemini():
    try:
        result = call_gemini("Hello! 이 문장은 정상적으로 응답하면 Gemini 연결 성공입니다.")
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ───────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)