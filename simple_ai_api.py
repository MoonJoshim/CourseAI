#!/usr/bin/env python3
"""
간단한 AI API 서버 (MongoDB 연결 없이)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

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

@app.route('/api/chat', methods=['POST'])
def chat():
    """AI 챗봇 대화 API (간단 버전)"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': '메시지를 입력해주세요'}), 400
        
        # 간단한 응답 생성
        if '데이터베이스' in user_message:
            response = "데이터베이스 강의는 실무에 매우 중요한 과목입니다. SQL과 NoSQL을 모두 다루며, 실습 위주의 수업이 많습니다. 팀프로젝트가 있는 경우가 많으니 참고하세요!"
        elif '웹프로그래밍' in user_message:
            response = "웹프로그래밍은 프론트엔드와 백엔드 개발을 모두 다루는 실용적인 과목입니다. HTML, CSS, JavaScript부터 React, Node.js까지 배울 수 있어 포트폴리오 작성에 도움이 됩니다."
        elif '노팀플' in user_message or '팀플' in user_message:
            response = "팀프로젝트가 없는 강의를 찾고 계시는군요! 일반적으로 이론 중심의 강의나 개인 과제 위주의 강의에서 팀프로젝트가 적습니다. 강의평을 확인해보시는 것을 추천드립니다."
        else:
            response = f"'{user_message}'에 대한 질문이군요! 실제로는 OpenAI GPT-4를 통해 더 정확하고 상세한 답변을 제공할 수 있습니다. 강의 검색 API와 연동하여 실시간 데이터를 바탕으로 답변드릴 수 있어요."
        
        return jsonify({
            'response': response,
            'timestamp': '2024-01-15T10:30:00Z',
            'function_called': None
        })
        
    except Exception as e:
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

@app.route('/api/health/db', methods=['GET'])
def health_db():
    """MongoDB 연결 헬스체크 (간단 버전)"""
    return jsonify({
        'ok': True, 
        'message': 'MongoDB 연결은 현재 비활성화 상태입니다. 간단한 AI API 서버가 실행 중입니다.',
        'status': 'simple_mode'
    })

if __name__ == '__main__':
    print("🤖 간단한 AI 챗봇 API 서버 시작")
    print("📍 http://localhost:5003")
    print("🧠 간단한 응답 모드 (OpenAI 연결 없음)")
    
    app.run(debug=True, host='0.0.0.0', port=5003)
