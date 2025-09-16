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

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    // 사용자 메시지 추가
    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    // AI 응답 시뮬레이션
    const aiResponse = {
      id: messages.length + 2,
      type: 'assistant',
      content: `"${inputMessage}"에 대한 답변입니다. 실제로는 AI API와 연동되어 강의 정보를 분석하고 답변을 제공합니다.`,
      timestamp: new Date()
    };

    setMessages([...messages, userMessage, aiResponse]);
    setInputMessage('');
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
            disabled={!inputMessage.trim()}
            className="px-6 py-3 bg-sky-600 hover:bg-sky-700 disabled:bg-slate-300 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            전송
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
