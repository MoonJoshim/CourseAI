import os, json
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import re

EMBED_PROVIDER = os.getenv("EMBED_PROVIDER", "gemini")
PROVIDER_DIM = {"openai": 1536, "gemini": 768}
EXPECTED_DIM = PROVIDER_DIM.get(EMBED_PROVIDER, 768)

from sentence_transformers import SentenceTransformer

# 멀티링구얼 한국어 강건성 높은 768d 임베딩 모델(E5)
model = SentenceTransformer("intfloat/multilingual-e5-base")

def embed_local(text: str):
    # E5 권장: passage 프리픽스 + 임베딩 정규화
    emb = model.encode([f"passage: {text}"], normalize_embeddings=True)[0]  # 768-d
    return emb.tolist()

def infer_has_team_project(text: str):
    # 간단한 규칙 기반 추론: 한국어 표현 위주
    neg_patterns = [
        r"(팀 ?플|팀 ?프로젝트|조별(?:과제|활동)).{0,12}(없|안 ?함|안함|미포함)",
        r"(없|안 ?함|안함|미포함).{0,12}(팀 ?플|팀 ?프로젝트|조별(?:과제|활동))",
        r"무 ?팀플",
        r"팀플\s*[xX✕×]",
    ]
    pos_patterns = [
        r"(팀 ?플|팀 ?프로젝트|조별(?:과제|활동)).{0,12}(있|함|진행|필수)",
        r"(있|함|진행|필수).{0,12}(팀 ?플|팀 ?프로젝트|조별(?:과제|활동))",
    ]
    neg = any(re.search(p, text) for p in neg_patterns)
    pos = any(re.search(p, text) for p in pos_patterns)
    if neg and not pos:
        return False
    if pos and not neg:
        return True
    return None

def main():
    load_dotenv()
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index_name = os.environ.get("INDEX_NAME", "courses-dev")
    dims = EXPECTED_DIM

    # 인덱스가 없을 때만 생성 (차원/메트릭은 콘솔 생성 값과 맞춰야 함!)
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=dims,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    index = pc.Index(index_name)

    # mock 데이터 읽기
    with open("mock_data.jsonl", "r", encoding="utf-8") as f:
        items = [json.loads(line) for line in f]

    vectors = []
    for r in items:
        e = embed_local(r["review_text"])
        assert len(e) == EXPECTED_DIM, f"Embedding dimension {len(e)} does not match index dimension {EXPECTED_DIM}. Check EMBED_PROVIDER and index settings."
        has_tp = r.get("has_team_project")
        if has_tp is None:
            has_tp = infer_has_team_project(r.get("review_text", ""))
        # Build metadata without None values (Pinecone forbids nulls)
        md = {
            "course_id": r["course_id"],
            "course_name": r["course_name"],
            "professor": r["professor"],
            "semester": r["semester"],
            "rating": float(r["rating"]) if r.get("rating") is not None else 0.0,
            "review_text": r["review_text"],
            "created_at": r["created_at"],
            "ingested_at": os.getenv("NOW_ISO") or "2025-09-23T00:00:00Z",
            "source": r.get("source", "mock"),
        }
        if has_tp is not None:
            md["has_team_project"] = bool(has_tp)

        vectors.append({
            "id": r["review_id"],
            "values": e,
            "metadata": md,
        })

    # 네임스페이스는 학기 기준을 추천
    ns = "ajou-2024_fall"
    index.upsert(vectors=vectors, namespace=ns)
    print(f"✅ Upsert {len(vectors)} vectors → index={index_name}, ns={ns}")

if __name__ == "__main__":
    main()