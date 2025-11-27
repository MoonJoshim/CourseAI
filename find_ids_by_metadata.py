#!/usr/bin/env python3
"""
Pinecone에서 metadata의 course_name이나 professor로 id를 찾는 스크립트

# 강의명으로 검색
python find_ids_by_metadata.py --course_name "데이터베이스"

# 교수명으로 검색
python find_ids_by_metadata.py --professor "김교수"

# 강의명과 교수명 모두로 검색
python find_ids_by_metadata.py --course_name "데이터베이스" --professor "김교수"

# 스캔 모드 사용 (더 정확하지만 느림)
python find_ids_by_metadata.py --course_name "데이터베이스" --scan

# 결과를 JSON 파일로 저장
python find_ids_by_metadata.py --course_name "데이터베이스" --output results.json

# 특정 인덱스와 namespace 지정
python find_ids_by_metadata.py --course_name "데이터베이스" --index "courses-dev" --namespace "reviews"
"""

import os
import sys
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone

# 환경변수 로드
load_dotenv()

def find_ids_by_metadata(
    course_name: Optional[str] = None,
    professor: Optional[str] = None,
    index_name: Optional[str] = None,
    namespace: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Pinecone에서 metadata로 id를 찾는 함수
    
    Args:
        course_name: 검색할 강의명 (부분 일치 가능)
        professor: 검색할 교수명 (부분 일치 가능)
        index_name: Pinecone 인덱스 이름 (기본값: 환경변수에서 가져옴)
        namespace: Pinecone namespace (기본값: None, _default_ 사용)
        limit: 최대 반환 개수
        
    Returns:
        List[Dict]: 찾은 id와 metadata 리스트
    """
    # 환경변수에서 설정 가져오기
    api_key = os.getenv('PINECONE_API_KEY')
    if not api_key:
        raise ValueError("PINECONE_API_KEY 환경변수가 설정되지 않았습니다.")
    
    if not index_name:
        index_name = os.getenv('PINECONE_INDEX', 'courses-dev')
    
    # Pinecone 초기화
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    # 인덱스 통계 확인 (차원 정보 필요)
    stats = index.describe_index_stats()
    dimension = stats.dimension
    
    print(f"🔍 Pinecone 인덱스: {index_name}")
    print(f"📊 총 벡터 수: {stats.total_vector_count}")
    print(f"📐 벡터 차원: {dimension}")
    
    # 필터 구성
    filter_dict = {}
    
    if course_name:
        # course_name 필터 (부분 일치를 위해 $regex 사용 불가, 정확한 일치만 가능)
        # Pinecone은 정확한 일치만 지원하므로, 여러 가능한 값으로 시도하거나
        # 모든 결과를 가져온 후 필터링하는 방법을 사용
        filter_dict['course_name'] = {"$eq": course_name}
        print(f"🔍 강의명 필터: {course_name}")
    
    if professor:
        if filter_dict:
            # 두 필터 모두 있는 경우 AND 조건
            filter_dict['professor'] = {"$eq": professor}
        else:
            filter_dict['professor'] = {"$eq": professor}
        print(f"🔍 교수명 필터: {professor}")
    
    # 더미 벡터 생성 (모든 차원을 0으로)
    dummy_vector = [0.0] * dimension
    
    # Query 옵션 구성
    query_options = {
        "vector": dummy_vector,
        "top_k": min(limit, 10000),  # Pinecone 최대 limit
        "include_metadata": True
    }
    
    if filter_dict:
        query_options["filter"] = filter_dict
    
    if namespace:
        query_options["namespace"] = namespace
        print(f"📦 Namespace: {namespace}")
    else:
        print(f"📦 Namespace: _default_")
    
    print(f"🔍 검색 시작...")
    
    try:
        # Query 실행
        results = index.query(**query_options)
        
        # 결과 처리
        found_ids = []
        for match in results.matches:
            metadata = match.metadata or {}
            
            # 필터링 (Pinecone 필터가 정확한 일치만 지원하므로, 부분 일치를 위해 추가 필터링)
            match_course = True
            match_professor = True
            
            if course_name:
                course_val = metadata.get('course_name', '')
                # 부분 일치 확인
                if course_name.lower() not in str(course_val).lower():
                    match_course = False
            
            if professor:
                prof_val = metadata.get('professor', '')
                # 부분 일치 확인
                if professor.lower() not in str(prof_val).lower():
                    match_professor = False
            
            if match_course and match_professor:
                found_ids.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": metadata
                })
        
        print(f"✅ {len(found_ids)}개의 ID를 찾았습니다.")
        return found_ids
        
    except Exception as e:
        print(f"❌ 검색 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return []


def find_all_ids_by_metadata_scan(
    course_name: Optional[str] = None,
    professor: Optional[str] = None,
    index_name: Optional[str] = None,
    namespace: Optional[str] = None,
    batch_size: int = 100
) -> List[Dict[str, Any]]:
    """
    Pinecone에서 모든 벡터를 스캔하여 metadata로 id를 찾는 함수
    (더 정확하지만 느림)
    
    Args:
        course_name: 검색할 강의명 (부분 일치)
        professor: 검색할 교수명 (부분 일치)
        index_name: Pinecone 인덱스 이름
        namespace: Pinecone namespace
        batch_size: 배치 크기
        
    Returns:
        List[Dict]: 찾은 id와 metadata 리스트
    """
    # 환경변수에서 설정 가져오기
    api_key = os.getenv('PINECONE_API_KEY')
    if not api_key:
        raise ValueError("PINECONE_API_KEY 환경변수가 설정되지 않았습니다.")
    
    if not index_name:
        index_name = os.getenv('PINECONE_INDEX', 'courses-dev')
    
    # Pinecone 초기화
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    # 인덱스 통계 확인
    stats = index.describe_index_stats()
    total_count = stats.total_vector_count
    
    print(f"🔍 Pinecone 인덱스: {index_name}")
    print(f"📊 총 벡터 수: {total_count}")
    print(f"🔍 스캔 모드로 검색 시작...")
    
    if namespace:
        print(f"📦 Namespace: {namespace}")
    else:
        print(f"📦 Namespace: _default_")
    
    found_ids = []
    
    # 더미 벡터로 모든 결과 가져오기
    dimension = stats.dimension
    dummy_vector = [0.0] * dimension
    
    # 큰 top_k로 모든 결과 가져오기 시도
    max_top_k = min(10000, total_count)
    
    try:
        query_options = {
            "vector": dummy_vector,
            "top_k": max_top_k,
            "include_metadata": True
        }
        
        if namespace:
            query_options["namespace"] = namespace
        
        results = index.query(**query_options)
        
        print(f"📥 {len(results.matches)}개의 결과를 가져왔습니다. 필터링 중...")
        
        # 필터링
        for match in results.matches:
            metadata = match.metadata or {}
            
            match_course = True
            match_professor = True
            
            if course_name:
                course_val = metadata.get('course_name', '')
                if course_name.lower() not in str(course_val).lower():
                    match_course = False
            
            if professor:
                prof_val = metadata.get('professor', '')
                if professor.lower() not in str(prof_val).lower():
                    match_professor = False
            
            if match_course and match_professor:
                found_ids.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": metadata
                })
        
        print(f"✅ {len(found_ids)}개의 ID를 찾았습니다.")
        return found_ids
        
    except Exception as e:
        print(f"❌ 검색 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Pinecone에서 metadata로 id 찾기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 강의명으로 검색
  python find_ids_by_metadata.py --course_name "데이터베이스"
  
  # 교수명으로 검색
  python find_ids_by_metadata.py --professor "김교수"
  
  # 강의명과 교수명 모두로 검색
  python find_ids_by_metadata.py --course_name "데이터베이스" --professor "김교수"
  
  # 스캔 모드 사용 (더 정확하지만 느림)
  python find_ids_by_metadata.py --course_name "데이터베이스" --scan
  
  # 특정 인덱스와 namespace 지정
  python find_ids_by_metadata.py --course_name "데이터베이스" --index "courses-dev" --namespace "reviews"
        """
    )
    
    parser.add_argument('--course_name', type=str, help='검색할 강의명 (부분 일치)')
    parser.add_argument('--professor', type=str, help='검색할 교수명 (부분 일치)')
    parser.add_argument('--index', type=str, help='Pinecone 인덱스 이름 (기본값: 환경변수에서)')
    parser.add_argument('--namespace', type=str, help='Pinecone namespace (기본값: _default_)')
    parser.add_argument('--limit', type=int, default=100, help='최대 반환 개수 (기본값: 100)')
    parser.add_argument('--scan', action='store_true', help='스캔 모드 사용 (모든 벡터 검색, 느리지만 정확)')
    parser.add_argument('--output', type=str, help='결과를 저장할 JSON 파일 경로')
    
    args = parser.parse_args()
    
    # 인자 검증
    if not args.course_name and not args.professor:
        parser.error("--course_name 또는 --professor 중 하나는 필수입니다.")
    
    # 검색 실행
    if args.scan:
        print("🔍 스캔 모드로 검색합니다...")
        results = find_all_ids_by_metadata_scan(
            course_name=args.course_name,
            professor=args.professor,
            index_name=args.index,
            namespace=args.namespace
        )
    else:
        results = find_ids_by_metadata(
            course_name=args.course_name,
            professor=args.professor,
            index_name=args.index,
            namespace=args.namespace,
            limit=args.limit
        )
    
    # 결과 출력
    if results:
        print(f"\n📋 찾은 ID 목록 ({len(results)}개):")
        print("=" * 80)
        
        for i, item in enumerate(results, 1):
            print(f"\n{i}. ID: {item['id']}")
            metadata = item.get('metadata', {})
            if 'course_name' in metadata:
                print(f"   강의명: {metadata['course_name']}")
            if 'professor' in metadata:
                print(f"   교수명: {metadata['professor']}")
            if 'semester' in metadata:
                print(f"   학기: {metadata['semester']}")
            if 'rating' in metadata:
                print(f"   평점: {metadata['rating']}")
        
        # JSON 파일로 저장
        if args.output:
            import json
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 결과가 {args.output}에 저장되었습니다.")
        
        # ID만 리스트로 출력
        print(f"\n📝 ID 목록만:")
        ids = [item['id'] for item in results]
        print(ids)
        
    else:
        print("\n❌ 검색 결과가 없습니다.")
        sys.exit(1)


if __name__ == '__main__':
    main()

