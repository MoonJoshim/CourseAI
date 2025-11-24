#!/usr/bin/env python3
"""Pinecone 인덱스에 저장된 강의평 정보 확인"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

# 환경변수 로드
load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX = os.getenv('PINECONE_INDEX', 'courses-dev')

if not PINECONE_API_KEY:
    print("❌ PINECONE_API_KEY가 설정되지 않았습니다.")
    exit(1)

try:
    # Pinecone 초기화
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # 인덱스 목록 확인
    print("📊 Pinecone 인덱스 목록:")
    indexes = pc.list_indexes()
    for idx in indexes:
        print(f"  - {idx.name}")
    
    # 지정된 인덱스 정보 확인
    if PINECONE_INDEX in [idx.name for idx in indexes]:
        print(f"\n✅ 인덱스 '{PINECONE_INDEX}' 존재")
        
        index = pc.Index(PINECONE_INDEX)
        stats = index.describe_index_stats()
        
        print(f"\n📈 인덱스 통계:")
        print(f"  - 총 벡터 수: {stats.total_vector_count}")
        print(f"  - 차원: {stats.dimension}")
        print(f"  - 네임스페이스: {list(stats.namespaces.keys()) if stats.namespaces else '없음'}")
        
        # 샘플 데이터 조회
        if stats.total_vector_count > 0:
            print(f"\n🔍 샘플 데이터 조회 (최대 3개):")
            try:
                # 임의의 쿼리로 샘플 데이터 가져오기
                results = index.query(
                    vector=[0.0] * stats.dimension,
                    top_k=3,
                    include_metadata=True
                )
                
                for i, match in enumerate(results.matches, 1):
                    print(f"\n  {i}. ID: {match.id}")
                    print(f"     Score: {match.score:.4f}")
                    if match.metadata:
                        print(f"     Metadata:")
                        for key, value in match.metadata.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"       - {key}: {value[:100]}...")
                            else:
                                print(f"       - {key}: {value}")
            except Exception as e:
                print(f"  ⚠️ 샘플 데이터 조회 실패: {e}")
    else:
        print(f"\n❌ 인덱스 '{PINECONE_INDEX}'가 존재하지 않습니다.")
        
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
