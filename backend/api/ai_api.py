#!/usr/bin/env python3
"""
에브리타임 AI 챗봇 API 서버
OpenAI GPT-4를 이용한 자연어 처리 및 Function Calling
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
import os
import json
import sys
from dotenv import load_dotenv
from datetime import datetime

# 기존 크롤링 모듈 import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.api.lecture_api import search_lecture, get_or_create_driver, ensure_logged_in

# 환경변수 로드
load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

# OpenAI 설정
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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

# Function Calling 정의
CHATBOT_FUNCTIONS = [
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

def handle_function_call(function_name, arguments):
    """Function Call 처리"""
    try:
        print(f"🔧 Function Call: {function_name} with args: {arguments}")
        
        if function_name == "search_lecture":
            keyword = arguments.get("keyword")
            if ensure_logged_in():
                driver = get_or_create_driver()
                results = search_lecture(driver, keyword)
                return {
                    "success": True,
                    "function": "search_lecture",
                    "keyword": keyword,
                    "results": results,
                    "count": len(results)
                }
            else:
                return {
                    "success": False,
                    "error": "로그인 실패"
                }
                
        elif function_name == "compare_lectures":
            keywords = arguments.get("keywords", [])
            all_results = {}
            
            if ensure_logged_in():
                driver = get_or_create_driver()
                for keyword in keywords:
                    results = search_lecture(driver, keyword)
                    all_results[keyword] = results
                
                return {
                    "success": True,
                    "function": "compare_lectures",
                    "keywords": keywords,
                    "results": all_results
                }
            else:
                return {
                    "success": False,
                    "error": "로그인 실패"
                }
                
        elif function_name == "get_recommendations":
            category = arguments.get("category")
            keywords = arguments.get("keywords", [])
            all_results = {}
            
            if ensure_logged_in():
                driver = get_or_create_driver()
                for keyword in keywords:
                    results = search_lecture(driver, keyword)
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
                    "error": "로그인 실패"
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
        
        # 대화 히스토리 구성
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # 이전 대화 히스토리 추가 (최근 5개만)
        for hist in conversation_history[-5:]:
            messages.append({"role": "user", "content": hist.get("user", "")})
            messages.append({"role": "assistant", "content": hist.get("assistant", "")})
        
        # 현재 사용자 메시지 추가
        messages.append({"role": "user", "content": user_message})
        
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            functions=CHATBOT_FUNCTIONS,
            function_call="auto",
            temperature=0.7,
            max_tokens=1000
        )
        
        message = response.choices[0].message
        
        # Function Call 처리
        if message.function_call:
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)
            
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
            final_response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            
            ai_response = final_response.choices[0].message.content
            
        else:
            # 일반 대화 응답
            ai_response = message.content
        
        print(f"🤖 AI 응답: {ai_response[:100]}...")
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'function_called': message.function_call.name if message.function_call else None
        })
        
    except Exception as e:
        print(f"❌ 챗봇 오류: {str(e)}")
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
    return '''
    <h1>🤖 에브리타임 AI 챗봇 API</h1>
    <p>OpenAI GPT-4를 이용한 강의평 전문 AI 어시스턴트</p>
    
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
    '''

if __name__ == '__main__':
    print("🤖 에브리타임 AI 챗봇 API 서버 시작")
    print("📍 http://localhost:5003")
    print("🧠 OpenAI GPT-4 Function Calling 활성화")
    
    app.run(debug=True, host='0.0.0.0', port=5003)
