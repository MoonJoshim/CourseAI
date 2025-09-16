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
    <div className="h-[calc(100vh-200px)] flex flex-col">
      {/* Search Header */}
      <div className="bg-white border-b border-slate-200 p-4 rounded-t-xl">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-sky-100 rounded-lg">
            <Search className="w-6 h-6 text-sky-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-800">AI 강의 검색</h2>
            <p className="text-sm text-slate-500">궁금한 강의 정보를 자연어로 검색하세요</p>
          </div>
          <span className="bg-sky-600 text-white text-xs px-2 py-1 rounded-full font-medium ml-auto">Beta</span>
        </div>
      </div>

      {/* Search Input */}
      <div className="bg-white border-b border-slate-200 p-4">
        <div className="relative">
          <input
            type="text"
            placeholder="예: 팀 프로젝트 없고 성적 잘 주는 소프트웨어학과 전공 강의 찾아줘"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 pr-12 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-400 focus:border-transparent bg-slate-50 focus:bg-white transition-colors"
          />
          <button className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 text-sky-600 hover:text-sky-700">
            <Search className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex flex-wrap gap-2 mt-3">
          <span className="text-sm text-slate-600">빠른 검색:</span>
          {['노팀플 강의', '성적 잘주는 교수', '재밌는 전공 강의', '실습 위주 수업'].map(tag => (
            <button
              key={tag}
              onClick={() => setSearchQuery(tag)}
              className="text-sm bg-sky-50 text-sky-700 px-3 py-1 rounded-full border border-sky-200 hover:bg-sky-100 transition-colors"
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white border-b border-slate-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex gap-1 p-1 bg-slate-100 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-colors ${viewMode === 'grid' ? 'bg-white text-sky-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-colors ${viewMode === 'list' ? 'bg-white text-sky-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-400 bg-white text-sm"
            >
              <option value="rating">평점 높은 순</option>
              <option value="popularity">인기 순</option>
              <option value="recent">최신 순</option>
              <option value="alphabetical">가나다 순</option>
            </select>
          </div>

          {/* Quick Stats */}
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1">
              <BookOpen className="w-4 h-4 text-sky-600" />
              <span className="text-slate-600">1,247개 강의</span>
            </div>
            <div className="flex items-center gap-1">
              <MessageSquare className="w-4 h-4 text-sky-600" />
              <span className="text-slate-600">15,892개 리뷰</span>
            </div>
          </div>
        </div>
      </div>

      {/* Course List */}
      <div className="flex-1 overflow-y-auto p-4 bg-slate-50">
        <div className={`grid gap-3 ${viewMode === 'grid' ? 'grid-cols-2' : 'grid-cols-1'}`}>
          {mockCourses.map(course => (
            <div key={course.id} className="bg-white border border-slate-200 rounded-lg p-4 hover:border-sky-200 transition-colors">
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-slate-800">{course.name}</h3>
                    <span className="text-sm text-slate-500">({course.courseCode})</span>
                    <button className={`p-1 rounded-full transition-colors ${course.bookmarked ? 'text-red-500' : 'text-slate-400 hover:text-red-400'}`}>
                      <Heart className={`w-4 h-4 ${course.bookmarked ? 'fill-current' : ''}`} />
                    </button>
                  </div>
                  <p className="text-sm text-slate-600">{course.professor} • {course.department}</p>
                  <p className="text-xs text-slate-500">{course.credits}학점 • {course.timeSlot}</p>
                </div>
                
                <div className="text-right">
                  <div className="flex items-center gap-1 mb-1">
                    <Star className="w-4 h-4 text-amber-400 fill-current" />
                    <span className="font-semibold text-slate-800">{course.rating}</span>
                  </div>
                  <div className="flex items-center gap-1 text-xs">
                    <TrendingUp className={`w-3 h-3 ${course.trend === 'up' ? 'text-emerald-500' : 'text-slate-400'}`} />
                    <span className="text-slate-500">{course.popularity}</span>
                  </div>
                </div>
              </div>

              {/* AI Summary */}
              <div className="bg-sky-50 rounded-lg p-3 mb-3 border border-sky-100">
                <div className="flex items-center gap-2 mb-1">
                  <Zap className="w-3 h-3 text-sky-600" />
                  <span className="text-xs font-medium text-sky-800">AI 요약</span>
                  <span className="text-xs bg-sky-200 text-sky-700 px-1.5 py-0.5 rounded">신뢰도 {course.sentiment}%</span>
                </div>
                <p className="text-xs text-sky-700">{course.aiSummary}</p>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-3">
                {course.tags.map((tag, index) => (
                  <span key={index} className="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded border border-slate-200">
                    {tag}
                  </span>
                ))}
              </div>

              <button 
                onClick={() => {
                  setSelectedCourse(course);
                  setCurrentPage('detail');
                }}
                className="w-full py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors text-sm font-medium"
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