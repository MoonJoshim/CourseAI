import React from 'react';
import { 
  Search, BookOpen, TrendingUp, Award, Calculator, Brain, Bell, User, MessageSquare
} from 'lucide-react';

const NavBar = ({ currentPage, setCurrentPage, mockUserProfile }) => {
  return (
    <div className="bg-white border-b border-slate-200 px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-8">
          <button 
            onClick={() => setCurrentPage('search')}
            className="flex items-center gap-3 hover:bg-slate-50 rounded-lg p-2 transition-colors"
          >
            <div className="bg-gradient-to-r from-sky-500 to-indigo-500 rounded-lg p-2">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-800">CourseAI</h1>
              <p className="text-xs text-slate-500">스마트 강의 분석</p>
            </div>
          </button>
          
          <nav className="flex gap-1">
            {[
              { id: 'search', label: 'AI 강의 검색', icon: Search },
              { id: 'chat', label: 'AI 채팅', icon: MessageSquare },
              { id: 'trends', label: '트렌드 분석', icon: TrendingUp },
              { id: 'recommend', label: '맞춤 추천', icon: Award },
              { id: 'gpa', label: '학점 계산', icon: Calculator }
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setCurrentPage(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    currentPage === tab.id 
                      ? 'bg-sky-50 text-sky-700 border border-sky-200' 
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <button className="p-2 text-slate-500 hover:text-slate-700 relative">
            <Bell className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
          </button>
          <button 
            onClick={() => setCurrentPage('profile')}
            className="flex items-center gap-3 hover:bg-slate-50 rounded-lg p-2 transition-colors"
          >
            <div className="w-8 h-8 bg-sky-500 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">{mockUserProfile.name}</p>
              <p className="text-xs text-slate-500">{mockUserProfile.major}</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default NavBar;
