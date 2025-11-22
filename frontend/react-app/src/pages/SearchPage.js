import React, { useState } from 'react';
import { 
  Search, BookOpen, MessageSquare, Zap, 
  Grid, List, Star, Heart, Loader
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
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState(null);

  // API 검색 함수
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      alert('검색어를 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await fetch(`http://localhost:5002/api/search?keyword=${encodeURIComponent(searchQuery)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setSearchResults(data.results || []);
    } catch (error) {
      console.error('검색 오류:', error);
      setError(error.message);
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Enter 키 처리
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };
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
            placeholder="강의명이나 교수명을 입력하세요 (예: 데이터베이스, 김교수)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            className="w-full px-4 py-3 pr-12 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-400 focus:border-transparent bg-slate-50 focus:bg-white transition-colors disabled:opacity-50"
          />
          <button 
            onClick={handleSearch}
            disabled={isLoading}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 text-sky-600 hover:text-sky-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? <Loader className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
          </button>
        </div>
        
        <div className="flex flex-wrap gap-2 mt-3">
          <span className="text-sm text-slate-600">빠른 검색:</span>
          {['데이터베이스', '웹프로그래밍', '소프트웨어공학', '알고리즘'].map(tag => (
            <button
              key={tag}
              onClick={async () => {
                setSearchQuery(tag);
                // 검색어 설정 후 검색 실행
                await new Promise(resolve => setTimeout(resolve, 50));
                if (!isLoading) {
                  handleSearch();
                }
              }}
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
        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader className="w-8 h-8 animate-spin text-sky-600 mx-auto mb-3" />
              <p className="text-slate-600">강의 정보를 검색하고 있습니다...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-800 font-medium">검색 중 오류가 발생했습니다</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
            <p className="text-red-600 text-sm">API 서버가 실행 중인지 확인해주세요.</p>
          </div>
        )}

        {/* No Results */}
        {hasSearched && !isLoading && !error && searchResults.length === 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-center">
            <p className="text-amber-800 font-medium">검색 결과가 없습니다</p>
            <p className="text-amber-600 text-sm mt-1">"{searchQuery}"에 대한 강의를 찾을 수 없습니다.</p>
          </div>
        )}

        {/* Search Results or Mock Data */}
        {!isLoading && (
          <div className={`grid gap-3 ${viewMode === 'grid' ? 'grid-cols-2' : 'grid-cols-1'}`}>
            {(hasSearched && searchResults.length > 0 ? searchResults : mockCourses).map((course, index) => {
              // API 응답과 Mock 데이터 구조 통일
              const courseData = hasSearched && searchResults.length > 0 ? {
                id: index,
                name: course.subject || course.name,
                courseCode: course.course_code || course.courseCode || '',
                professor: course.professor,
                department: course.department || '정보없음',
                credits: course.credits || 3,
                rating: course.rating || 0,
                reviewCount: course.reviews?.length || 0,
                tags: course.tags || [],
                aiSummary: course.ai_summary || '분석 중...',
                sentiment: course.sentiment || 0,
                bookmarked: false,
                trend: 'up',
                popularity: Math.floor(Math.random() * 100)
              } : course;

              return (
                <div key={courseData.id || index} className="bg-white border border-slate-200 rounded-lg p-4 hover:border-sky-200 transition-colors">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-slate-800">{courseData.name}</h3>
                        {courseData.courseCode && (
                          <span className="text-sm text-slate-500">({courseData.courseCode})</span>
                        )}
                        <button className={`p-1 rounded-full transition-colors ${courseData.bookmarked ? 'text-red-500' : 'text-slate-400 hover:text-red-400'}`}>
                          <Heart className={`w-4 h-4 ${courseData.bookmarked ? 'fill-current' : ''}`} />
                        </button>
                      </div>
                      <p className="text-sm text-slate-600">{courseData.professor} • {courseData.department}</p>
                      <p className="text-xs text-slate-500">{courseData.credits}학점</p>
                    </div>
                    
                    <div className="text-right">
                      <div className="flex items-center gap-1 mb-1">
                        <Star className="w-4 h-4 text-amber-400 fill-current" />
                        <span className="font-semibold text-slate-800">{courseData.rating}</span>
                      </div>
                      <div className="flex items-center gap-1 text-xs">
                        <MessageSquare className="w-3 h-3 text-slate-400" />
                        <span className="text-slate-500">{courseData.reviewCount}</span>
                      </div>
                    </div>
                  </div>

                  {/* AI Summary */}
                  {courseData.aiSummary && (
                    <div className="bg-sky-50 rounded-lg p-3 mb-3 border border-sky-100">
                      <div className="flex items-center gap-2 mb-1">
                        <Zap className="w-3 h-3 text-sky-600" />
                        <span className="text-xs font-medium text-sky-800">AI 요약</span>
                        {courseData.sentiment > 0 && (
                          <span className="text-xs bg-sky-200 text-sky-700 px-1.5 py-0.5 rounded">신뢰도 {courseData.sentiment}%</span>
                        )}
                      </div>
                      <p className="text-xs text-sky-700">{courseData.aiSummary}</p>
                    </div>
                  )}

                  {/* Tags */}
                  {courseData.tags && courseData.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {courseData.tags.map((tag, tagIndex) => (
                        <span key={tagIndex} className="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded border border-slate-200">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Reviews Preview */}
                  {hasSearched && course.reviews && course.reviews.length > 0 && (
                    <div className="bg-slate-50 rounded-lg p-3 mb-3 border border-slate-200">
                      <h4 className="text-xs font-medium text-slate-800 mb-2">최근 강의평</h4>
                      <div className="space-y-2">
                        {course.reviews.slice(0, 2).map((review, reviewIndex) => (
                          <div key={reviewIndex} className="text-xs">
                            <div className="flex items-center gap-1 mb-1">
                              <Star className="w-3 h-3 text-amber-400 fill-current" />
                              <span className="font-medium">{review.rating}점</span>
                              <span className="text-slate-500">• {review.semester}</span>
                            </div>
                            <p className="text-slate-700">{review.comment}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <button 
                    onClick={() => {
                      setSelectedCourse(courseData);
                      setCurrentPage('detail');
                    }}
                    className="w-full py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors text-sm font-medium"
                  >
                    상세 보기
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;