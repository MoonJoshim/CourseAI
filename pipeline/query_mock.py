import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# --- 설정 ---
INDEX_NAME = os.getenv("INDEX_NAME", "courses-dev")
NAMESPACE = os.getenv("PINE_NS", "ajou-2024_fall")
TOP_K = int(os.getenv("TOP_K", "5"))

# --- 로컬 임베딩 모델(768d) ---
model = SentenceTransformer("intfloat/multilingual-e5-base")

def embed_local(text: str):
    # E5 계열은 쿼리/패시지 프리픽스를 권장
    emb = model.encode([f"query: {text}"], normalize_embeddings=True)[0]  # 768-d
    return emb.tolist()
def build_filter():
    # 환경변수로 필터 토글
    meta_filter = {}
    if os.getenv("FILTER_PROF", "0") == "1":
        meta_filter["professor"] = {"$eq": "홍길동"}
    if os.getenv("FILTER_TEAMPL", "0") == "1":
        meta_filter["has_team_project"] = {"$eq": False}
    return meta_filter or None

def pretty_match(m):
    # Support both ScoredVector objects and plain dicts
    md = getattr(m, 'metadata', None)
    if md is None:
        md = m.get('metadata', {})
    score = getattr(m, 'score', None)
    if score is None:
        score = m.get('score', 0)
    return (
        f"[score={score:.3f}] "
        f"{md.get('course_name','?')} / {md.get('professor','?')} / {md.get('semester','?')}\n"
        f"  - {md.get('review_text','')}\n"
    )

def main():
    load_dotenv()
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(INDEX_NAME)

    # 예시 질의: 원하는 문장으로 바꿔가며 테스트
    query = os.getenv("QUERY", "홍길동 교수 강의 중 팀플 없는 수업")
    q_emb = embed_local(query)

    # (선택) 메타데이터 필터 예시: 교수명/팀플 등
    meta_filter = build_filter()

    res = index.query(
        vector=q_emb,
        top_k=TOP_K,
        namespace=NAMESPACE,
        filter=meta_filter,
        include_metadata=True,
        include_values=False,
    )

    # 진단: 매치가 없으면 필터/메타데이터 상태를 점검
    matches = getattr(res, 'matches', res.get('matches', []))
    if not matches and os.getenv("FILTER_TEAMPL", "0") == "1":
        print("\n⚠️  필터 결과가 비었습니다. 메타데이터에 has_team_project가 들어갔는지 점검합니다...")
        diag = index.query(
            vector=q_emb,
            top_k=min(5, TOP_K),
            namespace=NAMESPACE,
            filter=None,
            include_metadata=True,
            include_values=False,
        )
        diag_matches = getattr(diag, 'matches', diag.get('matches', []))
        if not diag_matches:
            print("   - 벡터는 존재하지만 이 쿼리와 유사한 문서가 없을 수 있습니다. 다른 쿼리로도 시도해보세요.")
        else:
            print("   - 상위 문서들의 has_team_project 값 미리보기:")
            for m in diag_matches:
                md = getattr(m, 'metadata', None) or m.get('metadata', {})
                print(f"     • {md.get('course_name','?')} / {md.get('professor','?')} → has_team_project={md.get('has_team_project')} | text='{md.get('review_text','')[:40]}…'")
        print("   - 만약 대부분 None/누락이면 upsert 스크립트를 최신으로 다시 실행해 주세요 (has_team_project 추론/저장 포함).\n")

    print(f"🔎 Query: {query}")
    if meta_filter:
        print(f"   Filter: {meta_filter}")
    print(f"   Top-{TOP_K} results\n")

    for i, m in enumerate(matches, 1):
        print(f"{i}. {pretty_match(m)}")

if __name__ == "__main__":
    main()