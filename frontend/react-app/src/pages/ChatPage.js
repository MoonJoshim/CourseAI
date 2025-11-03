import React, { useState } from 'react';
import { MessageSquare, Send, User, Brain } from 'lucide-react';

const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: '안녕하세요! 강의 관련 질문이 있으시면 언제든 물어보세요. 예를 들어 "노팀플 강의 추천해줘" 같은 질문을 해보시면 됩니다.',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5003';

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    // 사용자 메시지 추가
    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    // 기존 대화 히스토리를 API가 요구하는 형태로 변환
    const historyForApi = messages
      .filter(m => m.type === 'user' || m.type === 'assistant')
      .reduce((acc, m) => {
        const last = acc[acc.length - 1];
        if (m.type === 'user') {
          acc.push({ user: m.content, assistant: '' });
        } else {
          if (last && !last.assistant) {
            last.assistant = m.content;
          } else {
            acc.push({ user: '', assistant: m.content });
          }
        }
        return acc;
      }, []);

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      setIsSending(true);
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage.content,
          history: historyForApi
        })
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `API 오류 (status ${res.status})`);
      }

      const data = await res.json();
      const assistantMessage = {
        id: userMessage.id + 1,
        type: 'assistant',
        content: data.response || '응답이 비어 있습니다.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (e) {
      const errorMessage = {
        id: userMessage.id + 1,
        type: 'assistant',
        content: `요청 중 오류가 발생했어요: ${e.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  const quickQuestions = [
    '노팀플 강의 추천해줘',
    '성적 잘 주는 교수님은?',
    '웹개발 관련 강의 어때?',
    '컴공 전필 중에 쉬운 거는?'
  ];

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

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50">
        {messages.map((message) => (
          <div key={message.id} className={`flex items-start gap-3 ${message.type === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              message.type === 'user' 
                ? 'bg-sky-500' 
                : 'bg-slate-600'
            }`}>
              {message.type === 'user' ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Brain className="w-4 h-4 text-white" />
              )}
            </div>
            <div className={`max-w-2xl p-4 rounded-lg ${
              message.type === 'user'
                ? 'bg-sky-600 text-white rounded-tr-sm'
                : 'bg-white border border-slate-200 rounded-tl-sm'
            }`}>
              <p className={`text-sm leading-relaxed ${
                message.type === 'user' ? 'text-white' : 'text-slate-800'
              }`}>
                {message.content}
              </p>
              <p className={`text-xs mt-2 ${
                message.type === 'user' ? 'text-sky-100' : 'text-slate-500'
              }`}>
                {message.timestamp.toLocaleTimeString()}
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
            <Send className="w-4 h-4" />
            {isSending ? '전송 중...' : '전송'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
