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
# 프로젝트 루트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.api import get_mongo_db
from backend.api.lecture_api import search_lecture, get_or_create_driver, ensure_logged_in

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
    from google import genai
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
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
        
        # LLM Provider에 따라 다른 함수 호출
        if LLM_PROVIDER == 'openai':
            ai_response, function_called = chat_with_openai(user_message, conversation_history)
        elif LLM_PROVIDER == 'gemini':
            ai_response, function_called = chat_with_gemini(user_message, conversation_history)
        else:
            return jsonify({'error': f'지원하지 않는 LLM Provider: {LLM_PROVIDER}'}), 400
        
        print(f"🤖 AI 응답: {ai_response[:100]}...")
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'function_called': function_called,
            'llm_provider': LLM_PROVIDER
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
        <li><code>POST /api/chat</code> - AI 챗봇 대화</li>
        <li><code>GET /api/chat/test</code> - 테스트 페이지</li>
    </ul>
    
    <h2>예시 질문:</h2>
    <ul>
        <li>"데이터베이스 강의평 알려줘"</li>
        <li>"컴공에서 꿀강 추천해줘"</li>
        <li>"김교수님 강의 어떤지 궁금해"</li>
    </ul>
    
    <h2>설정 변경:</h2>
    <p>환경변수 <code>LLM_PROVIDER</code>를 설정하여 LLM을 변경할 수 있습니다 (gemini 또는 openai)</p>
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

if __name__ == '__main__':
    provider_name = "Gemini" if LLM_PROVIDER == "gemini" else "OpenAI GPT-4"
    print("🤖 에브리타임 AI 챗봇 API 서버 시작")
    print("📍 http://localhost:5003")
    print(f"🧠 {provider_name} Function Calling 활성화")
    print(f"🔧 LLM Provider: {LLM_PROVIDER.upper()}")
    
    app.run(debug=True, host='0.0.0.0', port=5003)
