import React, { useState, useRef } from 'react';
import { MessageSquare, Send, User, Brain, Info, PauseCircle } from 'lucide-react';

const CHAT_ENDPOINT = '/api/rag/chat';
// 기본값: 현재 도메인의 /api/rag/chat 으로 보냄 (Vercel rewrites가 백엔드로 프록시)
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

      const payload = { message: currentInput, history, top_k: DEFAULT_TOP_K };

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!res.ok) {
        const errorPayload = await res.json().catch(() => ({}));
        throw new Error(errorPayload.error || res.statusText);
      }

      const data = await res.json();

      const text =
        data.response || data.ai_response || data.error || '응답을 불러오지 못했습니다.';

      const aiResponse = {
        id: Date.now(),
        type: 'assistant',
        content: text,
        timestamp: new Date(),
        metadata: {
          provider: data.llm_provider || data.model || 'unknown',
          ragEnabled: Boolean(data.rag_enabled),
          topReviews: data.top_reviews || [],
        },
      };
      setMessages((prev) => [...prev, aiResponse]);
    } catch (e) {
      const aiResponse = {
        id: Date.now(),
        type: 'assistant',
        content: '서버와 통신 중 오류가 발생했어요. 잠시 후 다시 시도해주세요.',
        timestamp: new Date(),
        metadata: { error: e.message },
      };
      setMessages((prev) => [...prev, aiResponse]);
    } finally {
      clearTimeout(timeoutId);
      abortControllerRef.current = null;
      setIsSending(false);
    }
  };

  const quickQuestions = [
    '데이터베이스 강의 중 평점 높은 교수님은?',
    '노팀플이면서 과제 적당한 강의 추천해줘',
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
    <div className="min-h-screen" style={{background: 'linear-gradient(135deg, #D4F0F0 0%, #CCE2CB 100%)'}}>
      {/* Header */}
      <div className="bg-white border-b" style={{borderColor: '#B6CFB6'}}>
        <div className="max-w-6xl mx-auto px-6 py-5">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 mb-1">AI 채팅</h1>
            <p className="text-sm text-slate-600">강의에 대해 자연어로 질문하세요</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="max-w-6xl mx-auto px-6 py-5">
        <div className="bg-white rounded-lg border p-6 min-h-[500px] max-h-[600px] overflow-y-auto space-y-4" style={{borderColor: '#B6CFB6'}}>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start gap-3 ${
              message.type === 'user' ? 'flex-row-reverse' : ''
            }`}
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
              style={{backgroundColor: message.type === 'user' ? '#8FCACA' : '#B6CFB6'}}
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
                  ? 'text-white rounded-tr-sm shadow-sm'
                  : 'bg-white border rounded-tl-sm'
              }`}
              style={message.type === 'user' ? {background: 'linear-gradient(to right, #8FCACA, #97C1A9)'} : {borderColor: '#CCE2CB'}}
            >
              <p
                className={`text-sm leading-relaxed ${
                  message.type === 'user' ? 'text-white' : 'text-slate-800'
                } whitespace-pre-line`}
              >
                {message.content}
              </p>
              {message.metadata?.topReviews?.length ? (
                <div className="mt-3 text-xs text-slate-500 space-y-1">
                  <p className="font-medium text-slate-600">관련 강의평 근거</p>
                  <ul className="list-disc pl-4 space-y-1">
                    {message.metadata.topReviews.map((review, idx) => (
                      <li key={`${message.id}-review-${idx}`}>
                        <span className="font-semibold">{review.course_name}</span>{' '}
                        ({review.professor || '교수 정보 없음'}) – 평점 {review.rating ?? 'N/A'} /
                        유사도 {review.similarity_score}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {message.metadata?.provider ? (
                <p className="text-xs mt-2 text-slate-400">
                  모델: {message.metadata.provider}
                </p>
              ) : null}
              {message.metadata?.error ? (
                <p className="text-xs mt-2 text-rose-500">오류: {message.metadata.error}</p>
              ) : null}
              <p
                className={`text-xs mt-2 ${
                  message.type === 'user' ? 'text-white opacity-80' : 'text-slate-500'
                }`}
              >
                {formatTimestamp(message.timestamp)}
              </p>
            </div>
          </div>
        ))}

        {/* Recommended Prompts */}
        {messages.length === 1 && (
          <div className="mt-6 p-5 rounded-lg border" style={{backgroundColor: '#D4F0F0', borderColor: '#8FCACA'}}>
            <p className="text-sm font-semibold mb-4" style={{color: '#2C5F5F'}}>추천 프롬프트</p>
            <div className="grid grid-cols-2 gap-3">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInputMessage(question)}
                  className="text-sm bg-white text-slate-700 px-4 py-2.5 rounded-lg border transition-all text-left hover:shadow-md"
                  style={{borderColor: '#B6CFB6'}}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#CCE2CB';
                    e.target.style.borderColor = '#8FCACA';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = 'white';
                    e.target.style.borderColor = '#B6CFB6';
                  }}
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
        <div className="bg-white rounded-lg border p-4" style={{borderColor: '#B6CFB6'}}>
          <div className="flex items-end gap-3">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="강의에 대해 궁금한 점을 물어보세요"
                className="w-full resize-none border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 text-sm"
                style={{borderColor: '#B6CFB6'}}
                rows="2"
                onFocus={(e) => {
                  e.target.style.borderColor = '#8FCACA';
                  e.target.style.ringColor = '#8FCACA';
                }}
                onBlur={(e) => e.target.style.borderColor = '#B6CFB6'}
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
              className="px-5 py-2.5 disabled:bg-slate-300 text-white rounded-lg font-medium transition-all flex items-center gap-2 text-sm shadow-sm"
              style={{background: !inputMessage.trim() || isSending ? '#CBD5E1' : 'linear-gradient(to right, #8FCACA, #97C1A9)'}}
              onMouseEnter={(e) => {
                if (!e.target.disabled) {
                  e.target.style.background = 'linear-gradient(to right, #7AB8B8, #86B098)';
                }
              }}
              onMouseLeave={(e) => {
                if (!e.target.disabled) {
                  e.target.style.background = 'linear-gradient(to right, #8FCACA, #97C1A9)';
                }
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

