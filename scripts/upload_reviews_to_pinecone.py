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

    def embed_texts(self, texts: List[str], is_query: bool = False) -> List[List[float]]:
        """텍스트 리스트를 벡터로 변환
        
        Args:
            texts: 벡터화할 텍스트 리스트
            is_query: True이면 쿼리용 (E5 모델의 경우 "query:" 프리픽스 추가)
        """
        # E5 모델인 경우 쿼리/패시지 프리픽스 추가
        model_name = os.environ.get("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
        if "e5" in model_name.lower() or "multilingual-e5" in model_name.lower():
            if is_query:
                # 쿼리용: "query:" 프리픽스 추가
                prefixed_texts = [f"query: {text}" for text in texts]
            else:
                # 패시지용: "passage:" 프리픽스 추가 (저장 시와 동일하게)
                prefixed_texts = [f"passage: {text}" for text in texts]
        else:
            prefixed_texts = texts
        
        embeddings = self.embedder.encode(prefixed_texts, normalize_embeddings=True)
        return embeddings.tolist()

    def sanitize_id(self, text: str) -> str:
        """한글 등 비ASCII 문자를 안전한 ASCII ID로 변환"""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def upsert_reviews(self, review_items: List[Dict[str, Any]], namespace: Optional[str] = None) -> bool:
        """강의평 데이터를 Pinecone에 저장"""
        try:
            if not review_items:
                print("⚠️  저장할 강의평이 없습니다.")
                return False
            
            # 텍스트 추출 및 임베딩
            texts = [item["text"] for item in review_items]
            print(f"📝 벡터화할 텍스트 샘플: {texts[0][:50]}..." if texts else "❌ 텍스트 없음")
            vectors = self.embed_texts(texts)  # is_query=False (기본값)이므로 passage: 프리픽스 자동 추가
            
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
            if namespace:
                self.index.upsert(vectors=upsert_vectors, namespace=namespace)
                print(f"✅ {len(upsert_vectors)}개 강의평을 Pinecone에 저장했습니다. (namespace: {namespace})")
            else:
                self.index.upsert(vectors=upsert_vectors)
                print(f"✅ {len(upsert_vectors)}개 강의평을 Pinecone에 저장했습니다. (namespace: _default_)")
            return True
            
        except Exception as e:
            print(f"❌ Pinecone 업서트 실패: {e}")
            return False

    def query_similar_reviews(self, query_text: str, top_k: int = 10, 
                            filter_dict: Optional[Dict[str, Any]] = None,
                            namespace: Optional[str] = None) -> List[Dict]:
        """유사한 강의평 검색"""
        try:
            # 쿼리 텍스트 임베딩 (is_query=True로 설정하여 "query:" 프리픽스 자동 추가)
            query_vector = self.embed_texts([query_text], is_query=True)[0]
            
            # Pinecone 검색 옵션 구성
            query_options = {
                "vector": query_vector,
                "top_k": top_k,
                "include_metadata": True
            }
            
            # Namespace가 지정된 경우 추가
            if namespace:
                query_options["namespace"] = namespace
            
            # 필터가 있는 경우 추가
            if filter_dict:
                query_options["filter"] = filter_dict
            
            # Pinecone 검색
            results = self.index.query(**query_options)
            
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
        '유종빈': 'yoo_jongbin',
        '인공지능': 'artificial_intelligence'
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
        
        # 응답 구조 디버깅 정보 출력
        print(f"✅ cURL 응답 받기 완료")
        print(f"   응답 최상위 키: {list(response_data.keys())}")
        if 'result' in response_data:
            result_keys = list(response_data['result'].keys()) if isinstance(response_data['result'], dict) else 'not a dict'
            print(f"   result 키: {result_keys}")
            if isinstance(response_data['result'], dict) and 'articles' in response_data['result']:
                articles_count = len(response_data['result']['articles']) if isinstance(response_data['result']['articles'], list) else 0
                print(f"   articles 개수: {articles_count}")
                if articles_count > 0:
                    first_article = response_data['result']['articles'][0]
                    print(f"   첫 번째 article 키: {list(first_article.keys()) if isinstance(first_article, dict) else 'not a dict'}")
        
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

def get_existing_ids(vector_store: VectorStore, course_info: dict, namespace: Optional[str] = None) -> set:
    """
    Pinecone에서 기존에 저장된 ID 목록을 가져옴 (중복 검증용)
    
    Args:
        vector_store: VectorStore 인스턴스
        course_info: 강의 정보
        namespace: 검색할 namespace (None이면 _default_)
    
    Returns:
        set: 기존 ID 집합
    """
    try:
        # 강의명과 교수명으로 필터링하여 기존 데이터 조회
        course_name_ascii = korean_to_ascii(course_info['course_name'])
        professor_ascii = korean_to_ascii(course_info['professor'])
        prefix = f"{course_name_ascii}_{professor_ascii}_"
        
        # Pinecone에서 해당 강의의 모든 벡터 조회 (필터 사용)
        # 참고: Pinecone은 ID로 직접 조회할 수 없으므로, 메타데이터 필터로 조회
        existing_ids = set()
        
        # 메타데이터 필터로 기존 데이터 조회 시도
        try:
            results = vector_store.index.query(
                vector=[0.0] * 768,  # 더미 벡터 (필터만 사용)
                top_k=10000,  # 최대 개수
                include_metadata=True,
                filter={
                    "course_name": {"$eq": course_info['course_name']},
                    "professor": {"$eq": course_info['professor']}
                },
                namespace=namespace
            )
            
            for match in results.matches:
                existing_ids.add(match.id)
        except Exception as e:
            print(f"⚠️  기존 ID 조회 중 오류 (무시하고 계속): {e}")
        
        return existing_ids
    except Exception as e:
        print(f"⚠️  기존 ID 조회 실패 (무시하고 계속): {e}")
        return set()

def get_next_sequence_number(existing_ids: set, prefix: str) -> int:
    """
    기존 ID에서 다음 시퀀스 번호를 찾음
    
    Args:
        existing_ids: 기존 ID 집합
        prefix: ID 접두사 (예: "machine_learning_son_kyung_ah_")
    
    Returns:
        int: 다음 시퀀스 번호
    """
    max_num = -1
    for existing_id in existing_ids:
        if existing_id.startswith(prefix):
            try:
                # 접두사 뒤의 숫자 추출
                suffix = existing_id[len(prefix):]
                num = int(suffix)
                max_num = max(max_num, num)
            except ValueError:
                continue
    
    return max_num + 1

def create_review_items(api_response_data: dict, course_info: dict, vector_store: VectorStore, 
                        namespace: Optional[str] = None, check_duplicates: bool = True) -> list:
    """
    API 응답 데이터를 Pinecone 저장 형식으로 변환
    articles에서 id, year, semester, text, rate만 추출
    
    Args:
        api_response_data: 에브리타임 API 응답 데이터
        course_info: 강의 정보 (course_name, professor 필수)
        vector_store: VectorStore 인스턴스
        namespace: 검색할 namespace (중복 검증용)
        check_duplicates: 중복 검증 여부
    
    Returns:
        list: Pinecone 저장용 리뷰 아이템 리스트
    """
    review_items = []
    
    # 다양한 응답 형태 지원
    # 형태 1: {"result": {"articles": [...]}}
    # 형태 2: {"articles": [...]}
    # 형태 3: {"data": {"articles": [...]}}
    articles = []
    if "result" in api_response_data and isinstance(api_response_data["result"], dict):
        articles = api_response_data["result"].get("articles", [])
    elif "articles" in api_response_data:
        articles = api_response_data["articles"]
    elif "data" in api_response_data and isinstance(api_response_data["data"], dict):
        articles = api_response_data["data"].get("articles", [])
    
    if not articles:
        print("⚠️  articles를 찾을 수 없습니다. 응답 구조를 확인하세요.")
        print(f"   응답 최상위 키: {list(api_response_data.keys())}")
        return []
    
    print(f"📝 {len(articles)}개의 articles 처리 중...")
    
    # 중복 검증을 위한 기존 데이터 조회
    existing_ids = set()
    existing_original_ids = set()
    existing_texts = set()
    
    if check_duplicates:
        print("🔍 기존 데이터 조회 중 (중복 검증)...")
        existing_ids = get_existing_ids(vector_store, course_info, namespace)
        print(f"   기존 ID 개수: {len(existing_ids)}")
        
        # 기존 데이터의 original_id와 text도 조회 (중복 검증용)
        try:
            results = vector_store.index.query(
                vector=[0.0] * 768,
                top_k=10000,
                include_metadata=True,
                filter={
                    "course_name": {"$eq": course_info['course_name']},
                    "professor": {"$eq": course_info['professor']}
                },
                namespace=namespace
            )
            for match in results.matches:
                metadata = match.metadata
                if 'original_id' in metadata:
                    existing_original_ids.add(str(metadata['original_id']))
                if 'text' in metadata:
                    existing_texts.add(metadata['text'].strip())
        except Exception as e:
            print(f"⚠️  기존 메타데이터 조회 중 오류 (무시하고 계속): {e}")
    
    # ID 접두사 생성 (기존 패턴과 일치)
    course_name_ascii = korean_to_ascii(course_info['course_name'])
    professor_ascii = korean_to_ascii(course_info['professor'])
    id_prefix = f"{course_name_ascii}_{professor_ascii}_"
    
    # 다음 시퀀스 번호 찾기
    next_seq = get_next_sequence_number(existing_ids, id_prefix)
    current_seq = next_seq
    
    duplicate_count = 0
    
    for idx, article in enumerate(articles):
        # 필요한 필드만 추출: id, year, semester, text, rate
        article_id = article.get("id")
        year = article.get("year")
        semester = article.get("semester")
        text = article.get("text", "").strip()
        rate = article.get("rate")
        
        # 필수 필드 검증
        if None in [article_id, year, semester, rate]:
            print(f"⚠️  {idx}번째 article에서 필수 필드 누락, 건너뜀")
            continue
        
        # 텍스트가 비어있으면 건너뜀 (벡터화 불가)
        if not text:
            print(f"⚠️  {idx}번째 article에서 텍스트가 비어있음, 건너뜀")
            continue
        
        # 중복 검증
        if check_duplicates:
            # original_id로 중복 확인
            if str(article_id) in existing_original_ids:
                print(f"⚠️  {idx}번째 article 중복 (original_id: {article_id}), 건너뜀")
                duplicate_count += 1
                continue
            
            # 텍스트로 중복 확인
            if text in existing_texts:
                print(f"⚠️  {idx}번째 article 중복 (동일한 텍스트), 건너뜀")
                duplicate_count += 1
                continue
        
        # 벡터 ID 생성 (기존 패턴과 일치: machine_learning_son_kyung_ah_001 형식)
        review_id = f"{id_prefix}{current_seq:03d}"
        current_seq += 1
        
        # 학기 정보 정규화
        semester_normalized = f"{year}-{semester}"
        if semester == "여름" or semester == "summer":
            semester_normalized = f"{year}-summer"
        elif semester == "겨울" or semester == "winter":
            semester_normalized = f"{year}-winter"
        elif semester == "1" or semester == 1:
            semester_normalized = f"{year}-1"
        elif semester == "2" or semester == 2:
            semester_normalized = f"{year}-2"
        
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
    
    if check_duplicates and duplicate_count > 0:
        print(f"⚠️  총 {duplicate_count}개의 중복 강의평 건너뜀")
    
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
        "course_name": "강의명",  # 강의명 (필수)
        "professor": "교수명",      # 교수명 (필수)
        # "department": "소프트웨어학과",  # 학과 (선택사항)
    }
    
    # cURL 명령어 (여기에 실제 cURL 명령어를 입력하세요)
    # 여러 줄로 작성 가능 (백슬래시로 줄바꿈)
    curl_command = """curl 명령어"""
    
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
        
        # Namespace 설정 (기본값: _default_)
        namespace = os.getenv('PINE_NS') or None
        
        # API 응답 데이터 변환
        print("\n🔄 강의평 데이터 변환 중...")
        review_items = create_review_items(
            api_response_data, 
            course_info, 
            vector_store,
            namespace=namespace,
            check_duplicates=True  # 중복 검증 활성화
        )
        print(f"✅ {len(review_items)}개 강의평 데이터 변환 완료 (새로 추가될 데이터)")
        
        # Pinecone에 업로드
        print("📤 Pinecone에 업로드 중...")
        success = vector_store.upsert_reviews(review_items, namespace=namespace)
        
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
