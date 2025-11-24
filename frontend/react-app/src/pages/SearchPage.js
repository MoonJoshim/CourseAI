import React, { useState, useMemo } from 'react';
import { 
  Search, BookOpen, MessageSquare, Star, Filter
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
  const [selectedDepartment, setSelectedDepartment] = useState('전체');
  const [minRating, setMinRating] = useState(0);

  // 필터링 및 정렬된 강의 목록
  const filteredCourses = useMemo(() => {
    let filtered = [...mockCourses];

    // 검색어 필터
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(course => 
        course.name.toLowerCase().includes(query) ||
        course.professor.toLowerCase().includes(query) ||
        course.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // 학과 필터
    if (selectedDepartment !== '전체') {
      filtered = filtered.filter(course => course.department === selectedDepartment);
    }

    // 평점 필터
    if (minRating > 0) {
      filtered = filtered.filter(course => course.rating >= minRating);
    }

    // 정렬
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return b.rating - a.rating;
        case 'popularity':
          return b.reviewCount - a.reviewCount;
        case 'alphabetical':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

    return filtered;
  }, [mockCourses, searchQuery, selectedDepartment, minRating, sortBy]);

  // 고유 학과 목록
  const departments = useMemo(() => {
    const depts = new Set(mockCourses.map(c => c.department));
    return ['전체', ...Array.from(depts).sort()];
  }, [mockCourses]);

  // 통계
  const stats = useMemo(() => ({
    totalCourses: mockCourses.length,
    totalReviews: mockCourses.reduce((sum, c) => sum + c.reviewCount, 0),
    avgRating: (mockCourses.reduce((sum, c) => sum + c.rating, 0) / mockCourses.length).toFixed(1)
  }), [mockCourses]);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-5">
          <div className="mb-4">
            <h1 className="text-2xl font-bold text-slate-900 mb-1">과목별 강의평 조회</h1>
            <p className="text-sm text-slate-600">실제 수강생들의 강의평을 바탕으로 한 평가를 확인하세요</p>
          </div>

          {/* Stats */}
          <div className="flex gap-3 mb-4">
            <div className="flex-1 bg-slate-50 px-3 py-2.5 rounded-lg border border-slate-200">
              <div className="text-xs text-slate-600">전체 강의</div>
              <div className="text-lg font-bold text-slate-900">{stats.totalCourses}</div>
            </div>
            <div className="flex-1 bg-slate-50 px-3 py-2.5 rounded-lg border border-slate-200">
              <div className="text-xs text-slate-600">총 강의평</div>
              <div className="text-lg font-bold text-slate-900">{stats.totalReviews}</div>
            </div>
            <div className="flex-1 bg-slate-50 px-3 py-2.5 rounded-lg border border-slate-200">
              <div className="text-xs text-slate-600">평균 평점</div>
              <div className="text-lg font-bold text-slate-900">{stats.avgRating}</div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="text"
              placeholder="강의명, 교수명, 태그로 검색"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            />
          </div>

          {/* Filters */}
          <div className="flex gap-2 items-center">
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-sm"
            >
              {departments.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>

            <select
              value={minRating}
              onChange={(e) => setMinRating(Number(e.target.value))}
              className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-sm"
            >
              <option value={0}>모든 평점</option>
              <option value={4.5}>4.5점 이상</option>
              <option value={4.0}>4.0점 이상</option>
              <option value={3.5}>3.5점 이상</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-sm"
            >
              <option value="rating">평점순</option>
              <option value="popularity">리뷰순</option>
              <option value="alphabetical">가나다순</option>
            </select>

            <div className="ml-auto flex gap-2">
              <span className="text-xs text-slate-500 py-2">빠른 필터</span>
              {['노팀플', '과제많음', '성적잘줌', '쉬움'].map(tag => (
                <button
                  key={tag}
                  onClick={() => setSearchQuery(tag)}
                  className="px-2.5 py-1 bg-white border border-slate-200 rounded-full text-xs text-slate-700 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-all"
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-5">
        {/* Results Info */}
        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-slate-600">
            검색 결과 <span className="font-semibold text-slate-900">{filteredCourses.length}</span>개
          </p>
        </div>

        {/* Course Grid - 2 columns */}
        {filteredCourses.length === 0 ? (
          <div className="bg-white rounded-lg p-12 text-center border border-slate-200">
            <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-700 mb-1">검색 결과가 없습니다</h3>
            <p className="text-sm text-slate-500">다른 검색어를 시도해보세요</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredCourses.map((course) => (
              <div 
                key={course.id} 
                className="bg-white rounded-lg border border-slate-200 hover:border-blue-400 hover:shadow-sm transition-all duration-200"
              >
                {/* Header */}
                <div className="p-4 border-b border-slate-100">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="text-base font-bold text-slate-900 mb-1">{course.name}</h3>
                      <p className="text-sm text-slate-600">{course.professor}</p>
                      <p className="text-xs text-slate-500 mt-1">{course.department} • {course.credits}학점</p>
                    </div>
                    <div className="flex items-center gap-1 bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-200">
                      <Star className="w-4 h-4 text-blue-600 fill-current" />
                      <span className="text-base font-bold text-slate-900">{course.rating}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-slate-500">
                    <MessageSquare className="w-3 h-3" />
                    <span>{course.reviewCount}개 리뷰</span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-4">
                  {/* Tags */}
                  {course.tags && course.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-3">
                      {course.tags.map((tag, index) => (
                        <span 
                          key={index}
                          className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded border border-blue-200"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Summary */}
                  {course.aiSummary && (
                    <div className="bg-slate-50 rounded-lg p-3 mb-3 border border-slate-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-semibold text-slate-700">수강생 평가</span>
                        {course.sentiment > 0 && (
                          <span className="text-xs text-slate-500">신뢰도 {course.sentiment}%</span>
                        )}
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">{course.aiSummary}</p>
                    </div>
                  )}

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-2 mb-3">
                    <div className="text-center p-2 bg-slate-50 rounded border border-slate-200">
                      <div className="text-xs text-slate-500 mb-1">난이도</div>
                      <div className="text-xs font-semibold text-slate-700">
                        {course.difficulty || 3}/5
                      </div>
                    </div>
                    <div className="text-center p-2 bg-slate-50 rounded border border-slate-200">
                      <div className="text-xs text-slate-500 mb-1">과제량</div>
                      <div className="text-xs font-semibold text-slate-700">
                        {course.workload || 3}/5
                      </div>
                    </div>
                    <div className="text-center p-2 bg-slate-50 rounded border border-slate-200">
                      <div className="text-xs text-slate-500 mb-1">학점</div>
                      <div className="text-xs font-semibold text-slate-700">
                        {course.gradeGenerosity || 3}/5
                      </div>
                    </div>
                  </div>

                  {/* Button */}
                  <button 
                    onClick={() => {
                      setSelectedCourse(course);
                      setCurrentPage('detail');
                    }}
                    className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
                  >
                    상세보기
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {filteredCourses.length === 0 && searchQuery && (
          <div className="bg-white rounded-lg p-12 text-center border border-slate-200">
            <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-700 mb-1">검색 결과가 없습니다</h3>
            <p className="text-sm text-slate-500">다른 검색어를 시도해보세요</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
