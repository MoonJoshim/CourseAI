import React, { useState, useMemo } from 'react';
import { 
  Search, BookOpen, MessageSquare, Star, Filter, TrendingUp, Users, ThumbsUp
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">📚 과목별 강의평 조회</h1>
              <p className="text-slate-600">실제 수강생들의 강의평을 바탕으로 한 평가를 확인하세요</p>
            </div>
            <div className="flex gap-4 text-center">
              <div className="bg-sky-50 px-4 py-3 rounded-lg border border-sky-100">
                <div className="text-2xl font-bold text-sky-700">{stats.totalCourses}</div>
                <div className="text-xs text-sky-600">개 강의</div>
              </div>
              <div className="bg-purple-50 px-4 py-3 rounded-lg border border-purple-100">
                <div className="text-2xl font-bold text-purple-700">{stats.totalReviews}</div>
                <div className="text-xs text-purple-600">개 강의평</div>
              </div>
              <div className="bg-amber-50 px-4 py-3 rounded-lg border border-amber-100">
                <div className="text-2xl font-bold text-amber-700">{stats.avgRating}</div>
                <div className="text-xs text-amber-600">평균 평점</div>
              </div>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="강의명, 교수명, 태그로 검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
              />
            </div>
            
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
            >
              {departments.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>

            <select
              value={minRating}
              onChange={(e) => setMinRating(Number(e.target.value))}
              className="px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
            >
              <option value={0}>모든 평점</option>
              <option value={4.5}>4.5점 이상</option>
              <option value={4.0}>4.0점 이상</option>
              <option value={3.5}>3.5점 이상</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
            >
              <option value="rating">평점 높은 순</option>
              <option value="popularity">리뷰 많은 순</option>
              <option value="alphabetical">가나다 순</option>
            </select>
          </div>

          {/* Quick Filter Tags */}
          <div className="flex gap-2 mt-4">
            <span className="text-sm text-slate-600 py-2">빠른 필터:</span>
            {['노팀플', '과제많음', '성적잘줌', '쉬움'].map(tag => (
              <button
                key={tag}
                onClick={() => setSearchQuery(tag)}
                className="px-3 py-1.5 bg-white border border-slate-200 rounded-full text-sm text-slate-700 hover:bg-sky-50 hover:border-sky-300 hover:text-sky-700 transition-all"
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Course List */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Results Info */}
        <div className="mb-4 flex items-center justify-between">
          <p className="text-slate-600">
            <span className="font-semibold text-slate-900">{filteredCourses.length}개</span>의 강의가 검색되었습니다
          </p>
        </div>

        {/* Course Grid */}
        {filteredCourses.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center shadow-sm">
            <BookOpen className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-700 mb-2">검색 결과가 없습니다</h3>
            <p className="text-slate-500">다른 검색어나 필터를 시도해보세요</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredCourses.map((course) => (
              <div 
                key={course.id} 
                className="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden border border-slate-200 hover:border-sky-300"
              >
                {/* Header */}
                <div className="p-5 border-b border-slate-100">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-slate-900 mb-1">{course.name}</h3>
                      <p className="text-sm text-slate-600 mb-1">{course.professor} 교수님</p>
                      <p className="text-xs text-slate-500">{course.department} • {course.credits}학점</p>
                    </div>
                    <div className="flex flex-col items-end">
                      <div className="flex items-center gap-1 bg-amber-50 px-2 py-1 rounded-lg border border-amber-200">
                        <Star className="w-4 h-4 text-amber-500 fill-current" />
                        <span className="text-lg font-bold text-amber-700">{course.rating}</span>
                      </div>
                      <div className="flex items-center gap-1 mt-2 text-xs text-slate-500">
                        <MessageSquare className="w-3 h-3" />
                        <span>{course.reviewCount}개 리뷰</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="p-5">
                  {/* Tags */}
                  {course.tags && course.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {course.tags.map((tag, index) => (
                        <span 
                          key={index}
                          className="px-2.5 py-1 bg-gradient-to-r from-sky-50 to-blue-50 text-sky-700 text-xs font-medium rounded-full border border-sky-200"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* AI Summary */}
                  {course.aiSummary && (
                    <div className="bg-gradient-to-br from-sky-50 to-indigo-50 rounded-lg p-4 mb-4 border border-sky-200">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="p-1 bg-sky-500 rounded">
                          <ThumbsUp className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-xs font-semibold text-sky-800">수강생 평가 요약</span>
                        {course.sentiment > 0 && (
                          <span className="ml-auto text-xs bg-sky-600 text-white px-2 py-0.5 rounded-full">
                            신뢰도 {course.sentiment}%
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-slate-700 leading-relaxed">{course.aiSummary}</p>
                    </div>
                  )}

                  {/* Stats Row */}
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    <div className="text-center p-2 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">난이도</div>
                      <div className="text-sm font-semibold text-slate-700">
                        {'⭐'.repeat(course.difficulty || 3)}
                      </div>
                    </div>
                    <div className="text-center p-2 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">과제량</div>
                      <div className="text-sm font-semibold text-slate-700">
                        {'📝'.repeat(course.workload || 3)}
                      </div>
                    </div>
                    <div className="text-center p-2 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">성적</div>
                      <div className="text-sm font-semibold text-slate-700">
                        {'💯'.repeat(course.gradeGenerosity || 3)}
                      </div>
                    </div>
                  </div>

                  {/* Action Button */}
                  <button 
                    onClick={() => {
                      setSelectedCourse(course);
                      setCurrentPage('detail');
                    }}
                    className="w-full py-2.5 bg-gradient-to-r from-sky-600 to-blue-600 text-white rounded-lg hover:from-sky-700 hover:to-blue-700 transition-all font-medium text-sm shadow-sm hover:shadow"
                  >
                    상세 강의평 보기
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {filteredCourses.length === 0 && !searchQuery && (
          <div className="bg-white rounded-xl p-12 text-center shadow-sm">
            <BookOpen className="w-20 h-20 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-700 mb-2">강의평 데이터를 불러오는 중입니다</h3>
            <p className="text-slate-500">잠시만 기다려주세요...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
