import React, { useState, useRef } from 'react';
import { MessageSquare, Send, User, PauseCircle } from 'lucide-react';

// const CHAT_ENDPOINT = '/api/rag/chat';
const CHAT_ENDPOINT = '/api/v2/rag/chat';
const RAW_API_BASE = (process.env.REACT_APP_AI_API_BASE_URL || '').replace(/\/$/, '');
const API_BASE =
  typeof window !== 'undefined' &&
  window.location.protocol === 'https:' &&
  RAW_API_BASE.startsWith('http://')
    ? ''
    : RAW_API_BASE;
const REQUEST_TIMEOUT = Number(process.env.REACT_APP_AI_API_TIMEOUT || 20000);
const DEFAULT_TOP_K = Number(process.env.REACT_APP_AI_RAG_TOP_K || 5);

const formatTimestamp = (date) =>
  new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);

// 마크다운 텍스트를 HTML로 변환 (간단한 버전)
const renderMarkdown = (text) => {
  if (!text) return '';
  
  // **텍스트** -> <strong>텍스트</strong>
  let html = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  
  // *텍스트* -> <em>텍스트</em> (이탤릭)
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  
  // 줄바꿈 처리
  html = html.split('\n').map((line, idx) => {
    if (line.trim() === '') return '<br />';
    return line;
  }).join('\n');
  
  return html;
};

const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content:
        '안녕하세요! 저는 RAG(Retrieval-Augmented Generation) 기반의 강의평 AI 어시스턴트입니다.\n\n실제 수강생들의 강의평 데이터를 벡터 검색하여 가장 관련성 높은 정보를 기반으로 답변을 제공합니다.\n\n강의 추천, 교수님 정보, 수강 팁 등 궁금한 점을 자유롭게 질문해주세요.',
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const abortControllerRef = useRef(null);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    if (isSending) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');

    // 대화 히스토리 구성
    const history = messages
      .filter((m) => m.type === 'user' || m.type === 'assistant')
      .reduce((acc, m, idx, arr) => {
        if (m.type === 'user') {
          const next = arr[idx + 1];
          acc.push({
            user: m.content,
            assistant: next && next.type === 'assistant' ? next.content : '',
          });
        }
        return acc;
      }, []);

    const endpoint = API_BASE ? `${API_BASE}${CHAT_ENDPOINT}` : CHAT_ENDPOINT;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
    abortControllerRef.current = controller;

    try {
      setIsSending(true);
      // v2 API는 query와 history를 받습니다
      const payload = { query: currentInput, history };
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      // v2 API는 answer 필드를 반환합니다
      const content = data.answer || data.response || '응답을 받지 못했습니다.';
      const aiResponse = {
        id: Date.now(),
        type: 'assistant',
        content,
        timestamp: new Date(),
        metadata: {
          topReviews: data.top_reviews || [],
          provider: data.provider,
          debug: data.debug, // v2 API의 debug 정보
        },
      };
      setMessages((prev) => [...prev, aiResponse]);
    } catch (error) {
      clearTimeout(timeoutId);
      const errorMessage =
        error.name === 'AbortError'
          ? '요청 시간이 초과되었습니다. 다시 시도해주세요.'
          : '서버와 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
      const aiResponse = {
        id: Date.now(),
        type: 'assistant',
        content: errorMessage,
        timestamp: new Date(),
        metadata: { error: error.message },
      };
      setMessages((prev) => [...prev, aiResponse]);
    } finally {
      setIsSending(false);
      abortControllerRef.current = null;
    }
  };

  const quickQuestions = [
    '데이터베이스 강의 중 평점 높은 교수님은?',
    '팀플 없으면서 과제 적당한 강의 추천해줘',
    '웹 개발 배우기 좋은 강의는?',
    '알고리즘 강의 교수님별 차이점 알려줘',
    '객체지향프로그래밍 어느 교수님이 좋아?',
    '성적 잘 주시는 교수님 추천',
  ];

  const handleAbort = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-5">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 mb-1">AI 채팅</h1>
            <p className="text-sm text-slate-600">강의에 대해 자연어로 질문하세요</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="max-w-6xl mx-auto px-6 py-5">
        <div className="bg-white rounded-lg border border-slate-200 p-6 min-h-[500px] max-h-[600px] overflow-y-auto space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start gap-3 ${
              message.type === 'user' ? 'flex-row-reverse' : ''
            }`}
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
              style={{backgroundColor: message.type === 'user' ? '#8FCACA' : '#CBD5E1'}}
            >
              {message.type === 'user' ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <MessageSquare className="w-4 h-4 text-white" />
              )}
            </div>
            <div
              className={`max-w-2xl p-4 rounded-lg ${
                message.type === 'user'
                  ? 'bg-white border rounded-tr-sm shadow-sm'
                  : 'bg-slate-50 border border-slate-200 rounded-tl-sm'
              }`}
              style={
                message.type === 'user'
                  ? { borderColor: '#8FCACA', backgroundColor: '#FFFFFF' }
                  : {}
              }
            >
              <div
                className={`text-sm leading-relaxed ${
                  message.type === 'user' ? 'text-slate-900' : 'text-slate-800'
                } whitespace-pre-line`}
                dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }}
              />
              {message.metadata?.topReviews?.length ? (
                <div className="mt-3 text-xs text-slate-500 space-y-2">
                  <p className="font-medium text-slate-600">관련 강의평 근거</p>
                  <ul className="list-none space-y-2">
                    {message.metadata.topReviews.map((review, idx) => (
                      <li key={`${message.id}-review-${idx}`} className="border-l-2 border-slate-300 pl-3">
                        <div className="mb-1">
                          <span className="font-semibold text-slate-700">{review.course_name}</span>
                          {' '}({review.professor || '교수 정보 없음'})
                          {review.rating && (
                            <span className="ml-2 text-amber-600">★ {review.rating}</span>
                          )}
                        </div>
                        {review.text && (
                          <p className="text-slate-600 leading-relaxed italic">
                            "{review.text.length > 100 ? review.text.substring(0, 100) + '...' : review.text}"
                          </p>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
              <p
                className="text-xs mt-2 text-slate-500"
              >
                {formatTimestamp(message.timestamp)}
              </p>
            </div>
          </div>
        ))}

        {/* Recommended Prompts */}
        {messages.length === 1 && (
          <div
            className="mt-6 p-5 rounded-lg border"
            style={{ backgroundColor: '#E6F4F4', borderColor: '#B6E2E2' }}
          >
            <p className="text-sm font-semibold mb-4 text-slate-700">추천 프롬프트</p>
            <div className="grid grid-cols-2 gap-3">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInputMessage(question)}
                  className="text-sm text-slate-700 px-4 py-2.5 rounded-lg border transition-all text-left"
                  style={{ backgroundColor: '#F8FFFF', borderColor: '#B6E2E2' }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#E0F0F0')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#F8FFFF')}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}
        </div>
      </div>

      {/* Input */}
      <div className="max-w-6xl mx-auto px-6 pb-5">
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <div className="flex items-stretch gap-3">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="강의에 대해 궁금한 점을 물어보세요"
                className="w-full resize-none border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none text-sm h-full"
                rows="2"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isSending}
              className="px-6 disabled:bg-slate-300 text-white rounded-lg font-medium transition-all flex items-center justify-center gap-2 text-sm"
              style={{backgroundColor: !inputMessage.trim() || isSending ? '#CBD5E1' : '#8FCACA'}}
              onMouseEnter={(e) => {
                if (!e.target.disabled) e.target.style.backgroundColor = '#7AB8B8';
              }}
              onMouseLeave={(e) => {
                if (!e.target.disabled) e.target.style.backgroundColor = '#8FCACA';
              }}
            >
              {isSending ? (
                <PauseCircle className="w-4 h-4" onClick={handleAbort} />
              ) : (
                <Send className="w-4 h-4" />
              )}
              {isSending ? '대기중' : '전송'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
