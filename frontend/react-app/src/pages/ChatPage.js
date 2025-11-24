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
        '안녕하세요! 강의 관련 질문이 있으시면 언제든 물어보세요. 예를 들어 "노팀플 강의 추천해줘" 같은 질문을 해보시면 됩니다.',
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
    '노팀플 강의 추천해줘',
    '성적 잘 주는 교수님은?',
    '웹개발 관련 강의 어때?',
    '컴공 전필 중에 쉬운 거는?',
  ];

  const handleAbort = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/20 to-slate-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-white via-blue-50/10 to-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-5">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 mb-1">AI 채팅</h1>
            <p className="text-sm text-slate-600">강의에 대해 자연어로 질문하세요</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="max-w-6xl mx-auto px-6 py-5">
        <div className="bg-gradient-to-br from-white to-slate-50/50 rounded-lg border border-slate-200 p-6 min-h-[500px] max-h-[600px] overflow-y-auto space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start gap-3 ${
              message.type === 'user' ? 'flex-row-reverse' : ''
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.type === 'user' ? 'bg-blue-600' : 'bg-slate-600'
              }`}
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
                  ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-tr-sm shadow-sm'
                  : 'bg-white border border-slate-200 rounded-tl-sm'
              }`}
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
                  message.type === 'user' ? 'text-blue-100' : 'text-slate-500'
                }`}
              >
                {formatTimestamp(message.timestamp)}
              </p>
            </div>
          </div>
        ))}

        {/* Quick Questions */}
        {messages.length === 1 && (
          <div className="mt-4 p-4 bg-gradient-to-br from-blue-50 to-slate-50 rounded-lg border border-blue-200">
            <p className="text-sm text-slate-700 font-medium mb-3">빠른 질문</p>
            <div className="flex flex-wrap gap-2">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInputMessage(question)}
                  className="text-sm bg-white text-slate-700 px-3 py-1.5 rounded-full border border-slate-200 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-all"
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
          <div className="flex items-end gap-3">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="강의에 대해 궁금한 점을 물어보세요"
                className="w-full resize-none border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
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
              className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 disabled:bg-slate-300 text-white rounded-lg font-medium transition-all flex items-center gap-2 text-sm shadow-sm"
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

