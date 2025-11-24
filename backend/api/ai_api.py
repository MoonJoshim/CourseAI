#!/usr/bin/env python3
"""
에브리타임 AI 챗봇 API 서버
OpenAI GPT-4 또는 Google Gemini를 이용한 자연어 처리 및 Function Calling
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import sys
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Optional
import google.generativeai as genai
# 프로젝트 루트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.api import get_mongo_db
from backend.api.lecture_api import search_lecture, get_or_create_driver, ensure_logged_in

# VectorStore를 직접 파일 경로로 import하여 __init__.py의 database 초기화를 피함
VectorStore = None
vector_store = None
try:
    import importlib.util

    vector_store_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'vector_store.py')
    spec = importlib.util.spec_from_file_location("vector_store", vector_store_path)
    vector_store_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vector_store_module)
    VectorStore = getattr(vector_store_module, "VectorStore", None)

    if VectorStore is not None:
        try:
            vector_store = VectorStore()
            print("✅ Pinecone VectorStore 초기화 완료 (RAG 기능 활성화)")
        except Exception as e:  # pylint: disable=broad-except
            print(f"⚠️ VectorStore 초기화 실패: {e}")
            vector_store = None
    else:
        print("⚠️ VectorStore 클래스를 vector_store 모듈에서 찾을 수 없습니다. RAG 기능 비활성화.")
except Exception as e:  # pylint: disable=broad-except
    # sentence_transformers, pinecone 등이 설치되지 않아도 기본 챗봇은 동작하도록 RAG만 비활성화
    print(f"⚠️ VectorStore 모듈 로드 실패: {e}")
    VectorStore = None
    vector_store = None

# 환경변수 로드
load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

# LLM Provider 설정
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini').lower()  # 기본값: gemini

# LLM 설정
if LLM_PROVIDER == 'openai':
    import openai
    openai.api_key = os.getenv('OPENAI_API_KEY')
    openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
elif LLM_PROVIDER == 'gemini':
    # genai는 이미 14번 줄에서 import 되었음
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise ValueError(f"지원하지 않는 LLM Provider: {LLM_PROVIDER}. 'openai' 또는 'gemini'를 사용하세요.")

# 챗봇 시스템 프롬프트
SYSTEM_PROMPT = """
당신은 에브리타임 강의평 전문 AI 어시스턴트입니다.

🎯 **역할:**
- 대학생들의 수강신청을 도와주는 친근한 AI 비서
- 강의평 데이터를 바탕으로 객관적이고 유용한 정보 제공
- 개인의 학습 스타일과 목표를 고려한 맞춤 추천

💬 **대화 스타일:**
- 친근하고 도움이 되는 톤으로 대화
- 이모지를 적절히 사용하여 친근감 표현
- 복잡한 정보를 이해하기 쉽게 정리
- 궁금한 점이 있으면 언제든 물어보라고 격려

🔧 **기능:**
- 강의 검색 및 상세 정보 제공
- 강의 비교 및 추천
- 교수님별 강의 스타일 분석
- 수강 팁 및 조언 제공

사용자가 강의에 대해 질문하면, 적절한 함수를 호출하여 실시간 데이터를 가져온 후 친근하고 유용한 답변을 제공하세요.
"""

# RAG 챗봇 시스템 프롬프트
RAG_SYSTEM_PROMPT = """
당신은 에브리타임 강의평 전문 AI 어시스턴트입니다. Pinecone 벡터 데이터베이스에서 검색된 강의평 데이터를 바탕으로 정확하고 유용한 답변을 제공합니다.

🎯 **역할:**
- 대학생들의 수강신청을 도와주는 친근한 AI 비서
- 벡터 검색으로 찾은 강의평 데이터를 바탕으로 객관적이고 유용한 정보 제공
- 개인의 학습 스타일과 목표를 고려한 맞춤 추천

💬 **대화 스타일:**
- 친근하고 도움이 되는 톤으로 대화
- 이모지를 적절히 사용하여 친근감 표현
- 복잡한 정보를 이해하기 쉽게 정리
- 검색된 강의평 데이터를 근거로 답변

🔧 **중요 지침:**
- 제공된 강의평 컨텍스트를 기반으로 답변하세요
- 강의평 데이터에 없는 정보는 추측하지 마세요
- 여러 강의평의 의견을 종합하여 균형잡힌 답변을 제공하세요
- 구체적인 강의명, 교수명, 평점 등은 정확히 인용하세요
"""

# Function Calling 정의 (OpenAI 형식)
CHATBOT_FUNCTIONS_OPENAI = [
    {
        "name": "search_lecture",
        "description": "강의명이나 교수명으로 에브리타임에서 강의를 검색합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "검색할 강의명 또는 교수명"
                }
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "compare_lectures",
        "description": "여러 강의를 검색하여 비교 분석합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "비교할 강의명들의 배열"
                }
            },
            "required": ["keywords"]
        }
    },
    {
        "name": "get_recommendations",
        "description": "특정 조건에 맞는 강의 추천을 위해 관련 키워드로 검색합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "추천받고 싶은 분야나 카테고리 (예: 전공, 교양, 프로그래밍 등)"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "검색할 관련 키워드들"
                }
            },
            "required": ["category", "keywords"]
        }
    }
]

# Function Calling 정의 (Gemini 형식)
CHATBOT_TOOLS_GEMINI = [
    {
        "function_declarations": [
            {
                "name": "search_lecture",
                "description": "강의명이나 교수명으로 에브리타임에서 강의를 검색합니다",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "검색할 강의명 또는 교수명"
                        }
                    },
                    "required": ["keyword"]
                }
            },
            {
                "name": "compare_lectures",
                "description": "여러 강의를 검색하여 비교 분석합니다",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "비교할 강의명들의 배열"
                        }
                    },
                    "required": ["keywords"]
                }
            },
            {
                "name": "get_recommendations",
                "description": "특정 조건에 맞는 강의 추천을 위해 관련 키워드로 검색합니다",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "추천받고 싶은 분야나 카테고리 (예: 전공, 교양, 프로그래밍 등)"
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "검색할 관련 키워드들"
                        }
                    },
                    "required": ["category", "keywords"]
                }
            }
        ]
    }
]

def handle_function_call(function_name, arguments):
    """Function Call 처리"""
    try:
        print(f"🔧 Function Call: {function_name} with args: {arguments}")
        
        if function_name == "search_lecture":
            keyword = arguments.get("keyword")
            # DB에서 직접 검색 (크롤링 불필요)
            from backend.api.lecture_api import search_courses_from_db
            results = search_courses_from_db(keyword)
            return {
                "success": True,
                "function": "search_lecture",
                "keyword": keyword,
                "results": results,
                "count": len(results)
            }
                
        elif function_name == "compare_lectures":
            keywords = arguments.get("keywords", [])
            all_results = {}
            
            # DB에서 직접 검색 (크롤링 불필요)
            from backend.api.lecture_api import search_courses_from_db
            for keyword in keywords:
                results = search_courses_from_db(keyword)
                all_results[keyword] = results
            
            return {
                "success": True,
                "function": "compare_lectures",
                "keywords": keywords,
                "results": all_results
            }
                
        elif function_name == "get_recommendations":
            category = arguments.get("category")
            keywords = arguments.get("keywords", [])
            all_results = {}
            
            # DB에서 직접 검색 (크롤링 불필요)
            from backend.api.lecture_api import search_courses_from_db
            for keyword in keywords:
                results = search_courses_from_db(keyword)
                all_results[keyword] = results
            
            return {
                "success": True,
                "function": "get_recommendations",
                "category": category,
                "keywords": keywords,
                "results": all_results
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown function: {function_name}"
            }
            
    except Exception as e:
        print(f"❌ Function call error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def chat_with_openai(user_message, conversation_history):
    """OpenAI를 사용한 채팅"""
    # 대화 히스토리 구성
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # 이전 대화 히스토리 추가 (최근 5개만)
    for hist in conversation_history[-5:]:
        messages.append({"role": "user", "content": hist.get("user", "")})
        messages.append({"role": "assistant", "content": hist.get("assistant", "")})
    
    # 현재 사용자 메시지 추가
    messages.append({"role": "user", "content": user_message})
    
    # OpenAI API 호출
    response = openai_client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        functions=CHATBOT_FUNCTIONS_OPENAI,
        function_call="auto",
        temperature=0.7,
        max_tokens=1000
    )
    
    message = response.choices[0].message
    function_called = None
    
    # Function Call 처리
    if message.function_call:
        function_name = message.function_call.name
        function_args = json.loads(message.function_call.arguments)
        function_called = function_name
        
        print(f"🔧 Function Call 감지: {function_name}")
        
        # 함수 실행
        function_result = handle_function_call(function_name, function_args)
        
        # 함수 결과를 포함하여 최종 응답 생성
        messages.append({
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": function_name,
                "arguments": json.dumps(function_args)
            }
        })
        
        messages.append({
            "role": "function",
            "name": function_name,
            "content": json.dumps(function_result, ensure_ascii=False)
        })
        
        # 최종 응답 생성
        final_response = openai_client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        ai_response = final_response.choices[0].message.content
        
    else:
        # 일반 대화 응답
        ai_response = message.content
    
    return ai_response, function_called

def chat_with_gemini(user_message, conversation_history):
    """Gemini(google-genai 새 SDK)로 채팅"""
    # 시스템 프롬프트와 히스토리를 포함한 contents 구성
    prompt_lines = [SYSTEM_PROMPT.strip(), "", "이전 대화:"]
    for hist in conversation_history[-5:]:
        prompt_lines.append(f"사용자: {hist.get('user', '')}")
        if hist.get('assistant'):
            prompt_lines.append(f"어시스턴트: {hist.get('assistant', '')}")
    prompt_lines.append("")
    prompt_lines.append(f"사용자: {user_message}")
    contents = "\n".join(prompt_lines)

    # 단일 호출로 응답 생성 (기본: 최신 모델명 사용)
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
    )

    ai_response = getattr(response, 'text', None) or str(response)
    function_called = None
    return ai_response, function_called

# ========== RAG 관련 함수들 ==========

def format_context_from_reviews(reviews: List[Dict]) -> str:
    """검색된 강의평들을 컨텍스트 형식으로 포맷팅"""
    if not reviews:
        return "관련 강의평 데이터를 찾을 수 없습니다."
    
    context_parts = []
    context_parts.append("=== 검색된 강의평 컨텍스트 ===\n")
    
    for idx, review in enumerate(reviews[:5], 1):  # 상위 5개만 사용
        metadata = review.get('metadata', {})
        score = review.get('score', 0)
        
        course_name = metadata.get('course_name', '알 수 없음')
        professor = metadata.get('professor', '알 수 없음')
        rating = metadata.get('rating', 'N/A')
        # text와 review_text 둘 다 확인 (필드명 불일치 대응)
        review_text = metadata.get('text', '') or metadata.get('review_text', '')
        semester = metadata.get('semester', '')
        
        context_parts.append(f"[{idx}] 강의: {course_name}")
        context_parts.append(f"    교수: {professor}")
        context_parts.append(f"    학기: {semester}")
        context_parts.append(f"    평점: {rating}/5.0")
        context_parts.append(f"    강의평: {review_text}")
        context_parts.append(f"    유사도 점수: {score:.3f}")
        context_parts.append("")
    
    context_parts.append("=== 컨텍스트 끝 ===\n")
    return "\n".join(context_parts)

def chat_with_rag_openai(user_message: str, conversation_history: List[Dict], top_k: int = 5, namespace: Optional[str] = None):
    """OpenAI를 사용한 RAG 기반 채팅"""
    # 1. 사용자 질문을 벡터화하여 유사한 강의평 검색
    if vector_store:
        # namespace가 None이면 Pinecone이 자동으로 _default_를 사용
        actual_namespace = namespace if namespace else "_default_"
        print(f"🔍 Pinecone에서 유사한 강의평 검색 중... (top_k={top_k}, namespace={actual_namespace})")
        similar_reviews = vector_store.query_similar_reviews(user_message, top_k=top_k, namespace=namespace)
        print(f"✅ {len(similar_reviews)}개의 유사한 강의평을 찾았습니다.")
        
        # 컨텍스트 포맷팅
        context = format_context_from_reviews(similar_reviews)
    else:
        context = "⚠️ VectorStore가 초기화되지 않아 강의평 검색을 수행할 수 없습니다."
        similar_reviews = []
    
    # 2. 대화 히스토리 구성
    messages = [{"role": "system", "content": RAG_SYSTEM_PROMPT}]
    
    # 3. 컨텍스트를 시스템 메시지에 추가
    enhanced_system_prompt = f"{RAG_SYSTEM_PROMPT}\n\n{context}\n\n위의 강의평 컨텍스트를 바탕으로 사용자의 질문에 답변해주세요."
    messages[0]["content"] = enhanced_system_prompt
    
    # 4. 이전 대화 히스토리 추가 (최근 5개만)
    for hist in conversation_history[-5:]:
        messages.append({"role": "user", "content": hist.get("user", "")})
        messages.append({"role": "assistant", "content": hist.get("assistant", "")})
    
    # 5. 현재 사용자 메시지 추가
    messages.append({"role": "user", "content": user_message})
    
    # 6. OpenAI API 호출
    response = openai_client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=0.7,
        max_tokens=1500
    )
    
    ai_response = response.choices[0].message.content
    
    return ai_response, similar_reviews

def chat_with_rag_gemini(user_message: str, conversation_history: List[Dict], top_k: int = 5, namespace: Optional[str] = None):
    """Gemini를 사용한 RAG 기반 채팅"""
    # 1. 사용자 질문을 벡터화하여 유사한 강의평 검색
    if vector_store:
        # namespace가 None이면 Pinecone이 자동으로 _default_를 사용
        actual_namespace = namespace if namespace else "_default_"
        print(f"🔍 Pinecone에서 유사한 강의평 검색 중... (top_k={top_k}, namespace={actual_namespace})")
        similar_reviews = vector_store.query_similar_reviews(user_message, top_k=top_k, namespace=namespace)
        print(f"✅ {len(similar_reviews)}개의 유사한 강의평을 찾았습니다.")
        
        # 컨텍스트 포맷팅
        context = format_context_from_reviews(similar_reviews)
    else:
        context = "⚠️ VectorStore가 초기화되지 않아 강의평 검색을 수행할 수 없습니다."
        similar_reviews = []
    
    # 2. 프롬프트 구성
    prompt_lines = [RAG_SYSTEM_PROMPT.strip(), "", context, "", "이전 대화:"]
    
    for hist in conversation_history[-5:]:
        prompt_lines.append(f"사용자: {hist.get('user', '')}")
        if hist.get('assistant'):
            prompt_lines.append(f"어시스턴트: {hist.get('assistant', '')}")
    
    prompt_lines.append("")
    prompt_lines.append(f"사용자: {user_message}")
    prompt_lines.append("\n위의 강의평 컨텍스트를 바탕으로 사용자의 질문에 답변해주세요.")
    
    contents = "\n".join(prompt_lines)
    
    # 3. Gemini API 호출
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
    )
    
    ai_response = getattr(response, 'text', None) or str(response)
    
    return ai_response, similar_reviews

@app.route('/api/chat', methods=['POST'])
def chat():
    """AI 챗봇 대화 API"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': '메시지를 입력해주세요'}), 400
        
        print(f"💬 사용자 메시지: {user_message}")
        print(f"🤖 LLM Provider: {LLM_PROVIDER}")
        
        # 대화 히스토리 구성
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # 이전 대화 히스토리 추가 (최근 5개만)
        for hist in conversation_history[-5:]:
            messages.append({"role": "user", "content": hist.get("user", "")})
            messages.append({"role": "assistant", "content": hist.get("assistant", "")})
        
        # 현재 사용자 메시지 추가
        messages.append({"role": "user", "content": user_message})
        
        # Gemini API 호출 (단순 대화)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # 히스토리를 하나의 프롬프트로 연결
        history_text = "\n".join([
            f"사용자: {h.get('user','')}\n어시스턴트: {h.get('assistant','')}" for h in conversation_history[-5:]
        ])
        prompt = f"""
{SYSTEM_PROMPT}

이전 대화(있으면):
{history_text}

새 사용자 메시지:
{user_message}
""".strip()

        gen = model.generate_content(prompt)
        ai_response = gen.text if hasattr(gen, 'text') else str(gen)
        
        print(f"🤖 AI 응답: {ai_response[:100]}...")
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'model': 'gemini-1.5-flash'
        })
        
    except Exception as e:
        print(f"❌ 챗봇 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'챗봇 처리 중 오류 발생: {str(e)}'}), 500

@app.route('/api/chat/test', methods=['GET'])
def test_chat():
    """챗봇 테스트 엔드포인트"""
    test_messages = [
        "데이터베이스 강의평 알려줘",
        "컴공 추천 과목은?",
        "웹프로그래밍이랑 모바일프로그래밍 중에 뭐가 나을까?"
    ]
    
    return jsonify({
        'message': '챗봇 API가 정상 작동 중입니다!',
        'test_queries': test_messages,
        'endpoints': {
            'chat': 'POST /api/chat',
            'test': 'GET /api/chat/test'
        }
    })

@app.route('/')
def index():
    """메인 페이지"""
    provider_name = "Gemini" if LLM_PROVIDER == "gemini" else "OpenAI GPT-4"
    return f'''
    <h1>🤖 에브리타임 AI 챗봇 API</h1>
    <p><strong>{provider_name}</strong>를 이용한 강의평 전문 AI 어시스턴트</p>
    <p>현재 사용 중인 LLM: <strong>{LLM_PROVIDER.upper()}</strong></p>
    
    <h2>기능:</h2>
    <ul>
        <li>🔍 자연어로 강의 검색</li>
        <li>📊 강의 비교 및 분석</li>
        <li>💡 개인 맞춤 추천</li>
        <li>💬 대화형 인터페이스</li>
    </ul>
    
    <h2>사용법:</h2>
    <ul>
        <li><code>POST /api/chat</code> - AI 챗봇 대화 (기존 Function Calling 방식)</li>
        <li><code>POST /api/rag/chat</code> - RAG 기반 AI 챗봇 대화 (Pinecone 벡터 검색)</li>
        <li><code>GET /api/chat/test</code> - 테스트 페이지</li>
        <li><code>GET /api/rag/chat/test</code> - RAG 테스트 페이지</li>
        <li><code>GET /api/rag/health</code> - RAG 시스템 헬스체크</li>
    </ul>
    
    <h2>예시 질문:</h2>
    <ul>
        <li>"데이터베이스 강의평 알려줘"</li>
        <li>"컴공에서 꿀강 추천해줘"</li>
        <li>"김교수님 강의 어떤지 궁금해"</li>
    </ul>
    
    <h2>기존 API와 RAG API의 차이:</h2>
    <ul>
        <li><strong>/api/chat</strong>: Function Calling으로 MongoDB에서 실시간 검색</li>
        <li><strong>/api/rag/chat</strong>: Pinecone 벡터 검색으로 유사한 강의평을 찾아 컨텍스트로 활용</li>
    </ul>
    
    <h2>설정 변경:</h2>
    <p>환경변수 <code>LLM_PROVIDER</code>를 설정하여 LLM을 변경할 수 있습니다 (gemini 또는 openai)</p>
    <p>RAG 기능을 사용하려면 <code>PINECONE_API_KEY</code>와 <code>PINECONE_INDEX</code>를 설정하세요</p>
    '''

@app.route('/api/health/db', methods=['GET'])
def health_db():
    """MongoDB 연결 헬스체크"""
    try:
        db = get_mongo_db()
        result = db.command('ping')
        return jsonify({'ok': True, 'result': result}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

# ========== RAG 엔드포인트 ==========

@app.route('/api/rag/chat', methods=['POST'])
def rag_chat():
    """RAG 기반 AI 챗봇 대화 API (VectorStore 없으면 일반 챗봇으로 폴백)"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        conversation_history = data.get('history', [])
        top_k = data.get('top_k', 5)  # 검색할 강의평 개수 (기본값: 5)
        # Namespace: 지정하지 않으면 None (Pinecone이 자동으로 _default_ 사용)
        namespace = data.get('namespace') or os.getenv('PINE_NS') or None

        if not user_message:
            return jsonify({'error': '메시지를 입력해주세요'}), 400

        # VectorStore가 없으면 RAG 대신 일반 챗봇으로 폴백
        if not vector_store:
            print("⚠️ VectorStore 미초기화: 일반 LLM 챗봇으로 폴백합니다.")
            if LLM_PROVIDER == 'openai':
                ai_response, _ = chat_with_openai(user_message, conversation_history)
            elif LLM_PROVIDER == 'gemini':
                ai_response, _ = chat_with_gemini(user_message, conversation_history)
            else:
                return jsonify({'error': f'지원하지 않는 LLM Provider: {LLM_PROVIDER}'}), 400

            return jsonify({
                'response': ai_response,
                'timestamp': datetime.now().isoformat(),
                'llm_provider': LLM_PROVIDER,
                'rag_enabled': False,
                'reviews_found': 0,
                'top_reviews': []
            })

        print(f"💬 [RAG] 사용자 메시지: {user_message}")
        print(f"🤖 LLM Provider: {LLM_PROVIDER}")
        print(f"🔍 검색할 강의평 개수: {top_k}")
        # namespace가 None이면 Pinecone이 자동으로 _default_를 사용
        print(f"📦 Namespace: {namespace if namespace else '_default_ (자동)'}")

        # LLM Provider에 따라 다른 함수 호출
        if LLM_PROVIDER == 'openai':
            ai_response, similar_reviews = chat_with_rag_openai(user_message, conversation_history, top_k, namespace)
        elif LLM_PROVIDER == 'gemini':
            ai_response, similar_reviews = chat_with_rag_gemini(user_message, conversation_history, top_k, namespace)
        else:
            return jsonify({'error': f'지원하지 않는 LLM Provider: {LLM_PROVIDER}'}), 400

        print(f"🤖 [RAG] AI 응답: {ai_response[:100]}...")
        print(f"📊 검색된 강의평 개수: {len(similar_reviews)}")

        # 검색된 강의평의 메타데이터 정리 (민감한 정보 제외)
        review_summaries = []
        for review in similar_reviews[:3]:  # 상위 3개만 반환
            metadata = review.get('metadata', {})
            review_summaries.append({
                'course_name': metadata.get('course_name', ''),
                'professor': metadata.get('professor', ''),
                'rating': metadata.get('rating', 0),
                'similarity_score': round(review.get('score', 0), 3)
            })

        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'llm_provider': LLM_PROVIDER,
            'rag_enabled': True,
            'reviews_found': len(similar_reviews),
            'top_reviews': review_summaries
        })

    except Exception as e:
        print(f"❌ RAG 챗봇 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'RAG 챗봇 처리 중 오류 발생: {str(e)}'}), 500

@app.route('/api/rag/chat/test', methods=['GET'])
def test_rag_chat():
    """RAG 챗봇 테스트 엔드포인트"""
    test_messages = [
        "데이터베이스 강의평 알려줘",
        "컴공 추천 과목은?",
        "웹프로그래밍이랑 모바일프로그래밍 중에 뭐가 나을까?",
        "팀 프로젝트가 있는 강의 추천해줘"
    ]
    
    vector_store_status = "✅ 초기화됨" if vector_store else "❌ 초기화 실패"
    
    return jsonify({
        'message': 'RAG 챗봇 API가 정상 작동 중입니다!',
        'vector_store_status': vector_store_status,
        'llm_provider': LLM_PROVIDER,
        'test_queries': test_messages,
        'endpoints': {
            'rag_chat': 'POST /api/rag/chat',
            'test': 'GET /api/rag/chat/test',
            'health': 'GET /api/rag/health'
        }
    })

@app.route('/api/rag/health', methods=['GET'])
def rag_health():
    """RAG 시스템 헬스체크"""
    try:
        health_status = {
            'vector_store': False,
            'llm_provider': LLM_PROVIDER,
            'pinecone_index': None,
            'index_stats': None
        }
        
        if vector_store:
            health_status['vector_store'] = True
            health_status['pinecone_index'] = vector_store.index_name
            try:
                stats = vector_store.get_index_stats()
                health_status['index_stats'] = stats
            except Exception as e:
                health_status['index_stats_error'] = str(e)
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'vector_store': False
        }), 500

if __name__ == '__main__':
    provider_name = "Gemini" if LLM_PROVIDER == "gemini" else "OpenAI GPT-4"
    vector_status = "✅ 연결됨" if vector_store else "❌ 연결 실패"
    
    print("🤖 에브리타임 AI 챗봇 API 서버 시작")
    print("📍 http://localhost:5003")
    print(f"🔧 LLM Provider: {LLM_PROVIDER.upper()}")
    print(f"📊 Pinecone VectorStore: {vector_status}")
    if vector_store:
        print(f"   - 인덱스: {vector_store.index_name}")
        print("   - RAG 엔드포인트: POST /api/rag/chat")
    
    app.run(debug=True, host='0.0.0.0', port=5003)
