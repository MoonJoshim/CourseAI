import React from 'react';
import { 
  Search, Brain, BookOpen, MessageSquare, Users, Zap, 
  Grid, List, Star, TrendingUp, Heart
} from 'lucide-react';

const SearchPage = ({ 
  searchQuery, 
  setSearchQuery, 
  viewMode, 
  setViewMode, 
  sortBy, 
  setSortBy,
  mockCourses,
  setSelectedCourse,
  setCurrentPage
}) => {
  return (
    <div className="space-y-6">
      {/* AI Search Box */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-100">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-6">
            <Brain className="text-blue-600 w-8 h-8" />
            <h2 className="text-2xl font-bold text-gray-800">AI 강의 검색</h2>
            <span className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-sm px-3 py-1 rounded-full">
              Beta
            </span>
          </div>
          
          <div className="relative mb-4">
            <input
              type="text"
              placeholder="예: 팀 프로젝트 없고 성적 잘 주는 소프트웨어학과 전공 강의 찾아줘"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-6 py-4 pr-16 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
            />
            <button className="absolute right-3 top-1/2 transform -translate-y-1/2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <Search className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-600 mr-2">인기 검색:</span>
            {['노팀플 강의', '성적 잘주는 교수', '재밌는 전공 강의', '실습 위주 수업'].map(tag => (
              <button
                key={tag}
                onClick={() => setSearchQuery(tag)}
                className="text-sm bg-white px-3 py-1 rounded-full border hover:bg-blue-50 hover:border-blue-200 transition-colors"
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-6">
        {[
          { label: '분석된 강의', value: '1,247개', icon: BookOpen, color: 'blue' },
          { label: '강의평', value: '15,892개', icon: MessageSquare, color: 'green' },
          { label: '활성 사용자', value: '3,421명', icon: Users, color: 'purple' },
          { label: 'AI 분석', value: '실시간', icon: Zap, color: 'orange' }
        ].map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center gap-4">
                <div className={`bg-${stat.color}-100 rounded-lg p-3`}>
                  <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
                <div>
                  <p className="text-sm text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Filters and Sort */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">강의 목록</h3>
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="rating">평점 높은 순</option>
              <option value="popularity">인기 순</option>
              <option value="recent">최신 순</option>
              <option value="alphabetical">가나다 순</option>
            </select>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="flex gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
          <select className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">전체 학과</option>
            <option value="software">소프트웨어학과</option>
            <option value="computer">컴퓨터공학과</option>
            <option value="ai">AI학과</option>
          </select>
          
          <select className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">강의 유형</option>
            <option value="major">전공필수</option>
            <option value="elective">전공선택</option>
            <option value="general">교양</option>
          </select>
          
          <select className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">학점</option>
            <option value="1">1학점</option>
            <option value="2">2학점</option>
            <option value="3">3학점</option>
          </select>
          
          <button className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg text-sm">
            필터 초기화
          </button>
        </div>

        {/* Course Grid */}
        <div className={`grid gap-6 ${viewMode === 'grid' ? 'grid-cols-2' : 'grid-cols-1'}`}>
          {mockCourses.map(course => (
            <div key={course.id} className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-bold text-gray-900">{course.name}</h3>
                    <span className="text-sm text-gray-500">({course.courseCode})</span>
                    <button 
                      className={`p-1 rounded-full ${course.bookmarked ? 'text-red-500' : 'text-gray-400 hover:text-red-500'}`}
                    >
                      <Heart className={`w-4 h-4 ${course.bookmarked ? 'fill-current' : ''}`} />
                    </button>
                  </div>
                  <p className="text-gray-600 mb-1">{course.professor} • {course.department}</p>
                  <p className="text-sm text-gray-500">{course.credits}학점 • {course.timeSlot} • {course.room}</p>
                </div>
                
                <div className="text-right">
                  <div className="flex items-center gap-1 mb-1">
                    <Star className="w-4 h-4 text-yellow-500 fill-current" />
                    <span className="font-bold">{course.rating}</span>
                    <span className="text-sm text-gray-500">({course.reviewCount})</span>
                  </div>
                  <div className="flex items-center gap-1 text-sm">
                    <TrendingUp className={`w-4 h-4 ${course.trend === 'up' ? 'text-green-500' : 'text-red-500'}`} />
                    <span className="text-gray-500">인기도 {course.popularity}</span>
                  </div>
                </div>
              </div>

              {/* AI Summary */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 mb-4 border border-purple-100">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-4 h-4 text-purple-600" />
                  <span className="text-sm font-semibold text-purple-800">AI 요약</span>
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">신뢰도 {course.sentiment}%</span>
                </div>
                <p className="text-sm text-gray-700">{course.aiSummary}</p>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-2 mb-4">
                {course.tags.map((tag, index) => (
                  <span key={index} className="bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full">
                    {tag}
                  </span>
                ))}
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-100 text-center text-sm">
                <div>
                  <p className="text-gray-500">난이도</p>
                  <div className="flex justify-center gap-1 mt-1">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className={`w-2 h-2 rounded-full ${i < course.difficulty ? 'bg-orange-400' : 'bg-gray-200'}`} />
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-gray-500">과제량</p>
                  <div className="flex justify-center gap-1 mt-1">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className={`w-2 h-2 rounded-full ${i < course.workload ? 'bg-red-400' : 'bg-gray-200'}`} />
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-gray-500">성적</p>
                  <div className="flex justify-center gap-1 mt-1">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className={`w-2 h-2 rounded-full ${i < course.gradeGenerosity ? 'bg-green-400' : 'bg-gray-200'}`} />
                    ))}
                  </div>
                </div>
              </div>

              <button 
                onClick={() => {
                  setSelectedCourse(course);
                  setCurrentPage('detail');
                }}
                className="w-full mt-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                상세 보기
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SearchPage;
