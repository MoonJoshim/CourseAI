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
    <div className="h-[calc(100vh-200px)] flex flex-col">
      {/* Chat Header */}
      <div className="bg-white border-b border-slate-200 p-4 rounded-t-xl">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-sky-100 rounded-lg">
            <MessageSquare className="w-6 h-6 text-sky-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-800">AI 강의 상담</h2>
            <p className="text-sm text-slate-500">궁금한 강의 정보를 자연어로 물어보세요</p>
          </div>
        </div>
      </div>

      {/* Mode Toggle */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <Info className="w-4 h-4" />
          <span>RAG 모드: 강의평 벡터 검색을 사용해 더 정확한 답변을 제공합니다.</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start gap-3 ${
              message.type === 'user' ? 'flex-row-reverse' : ''
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.type === 'user' ? 'bg-sky-500' : 'bg-slate-600'
              }`}
            >
              {message.type === 'user' ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Brain className="w-4 h-4 text-white" />
              )}
            </div>
            <div
              className={`max-w-2xl p-4 rounded-lg ${
                message.type === 'user'
                  ? 'bg-sky-600 text-white rounded-tr-sm'
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
                  message.type === 'user' ? 'text-sky-100' : 'text-slate-500'
                }`}
              >
                {formatTimestamp(message.timestamp)}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Questions */}
      {messages.length === 1 && (
        <div className="p-4 bg-white border-t border-slate-200">
          <p className="text-sm text-slate-600 mb-3">빠른 질문:</p>
          <div className="flex flex-wrap gap-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(question)}
                className="text-sm bg-sky-50 text-sky-700 px-3 py-2 rounded-full border border-sky-200 hover:bg-sky-100 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-slate-200 p-4 rounded-b-xl">
        <div className="flex items-end gap-3">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="강의에 대해 궁금한 점을 물어보세요..."
              className="w-full resize-none border border-slate-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-sky-400 focus:border-transparent bg-slate-50 focus:bg-white transition-colors"
              rows="1"
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
            className="px-6 py-3 bg-sky-600 hover:bg-sky-700 disabled:bg-slate-300 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            {isSending ? (
              <PauseCircle className="w-4 h-4" onClick={handleAbort} />
            ) : (
              <Send className="w-4 h-4" />
            )}
            {isSending ? '응답 대기 중...' : '전송'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;

