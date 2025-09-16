import React from 'react';
import { 
  Search, BookOpen, TrendingUp, Award, Calculator, Brain, Bell, User
} from 'lucide-react';

const NavBar = ({ currentPage, setCurrentPage, mockUserProfile }) => {
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-2">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI 강의 검색</h1>
              <p className="text-sm text-gray-500">스마트 강의 분석 플랫폼</p>
            </div>
          </div>
          
          <nav className="flex gap-1">
            {[
              { id: 'search', label: '강의 검색', icon: Search },
              { id: 'detail', label: '강의 상세', icon: BookOpen },
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
                      ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
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
          <button className="p-2 text-gray-500 hover:text-gray-700 relative">
            <Bell className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
          </button>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold">{mockUserProfile.name}</p>
              <p className="text-xs text-gray-500">{mockUserProfile.major}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NavBar;
