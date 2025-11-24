import React, { useState, useMemo } from 'react';
import { 
  Search, BookOpen, MessageSquare, Star
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

  return (
    <div className="min-h-screen" style={{background: 'linear-gradient(135deg, #D4F0F0 0%, #CCE2CB 100%)'}}>
      {/* Header */}
      <div className="bg-white border-b" style={{borderColor: '#B6CFB6'}}>
        <div className="max-w-6xl mx-auto px-6 py-5">
          <div className="mb-5">
            <h1 className="text-2xl font-bold text-slate-900 mb-1">과목별 강의평 조회</h1>
            <p className="text-sm text-slate-600">실제 수강생들의 강의평을 바탕으로 한 평가를 확인하세요</p>
          </div>

          {/* Search Bar */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="text"
              placeholder="강의명, 교수명, 태그로 검색"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 text-sm"
              style={{borderColor: '#B6CFB6'}}
              onFocus={(e) => e.target.style.borderColor = '#8FCACA'}
              onBlur={(e) => e.target.style.borderColor = '#B6CFB6'}
            />
          </div>

          {/* Filters */}
          <div className="flex gap-4 items-center">
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="px-4 py-2.5 border rounded-lg focus:outline-none bg-white text-sm min-w-[140px]"
              style={{borderColor: '#B6CFB6'}}
            >
              {departments.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>

            <select
              value={minRating}
              onChange={(e) => setMinRating(Number(e.target.value))}
              className="px-4 py-2.5 border rounded-lg focus:outline-none bg-white text-sm min-w-[140px]"
              style={{borderColor: '#B6CFB6'}}
            >
              <option value={0}>모든 평점</option>
              <option value={4.5}>4.5점 이상</option>
              <option value={4.0}>4.0점 이상</option>
              <option value={3.5}>3.5점 이상</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2.5 border rounded-lg focus:outline-none bg-white text-sm min-w-[140px]"
              style={{borderColor: '#B6CFB6'}}
            >
              <option value="rating">평점순</option>
              <option value="popularity">리뷰순</option>
              <option value="alphabetical">가나다순</option>
            </select>

            <div className="ml-auto flex gap-3 items-center pr-2">
              {['노팀플', '과제많음', '성적잘줌', '쉬움'].map(tag => (
                <button
                  key={tag}
                  onClick={() => setSearchQuery(tag)}
                  className="px-4 py-1.5 bg-white border rounded-full text-xs text-slate-700 hover:text-slate-900 transition-all font-medium"
                  style={{borderColor: '#B6CFB6'}}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#D4F0F0';
                    e.target.style.borderColor = '#8FCACA';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = 'white';
                    e.target.style.borderColor = '#B6CFB6';
                  }}
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
        <div className="mb-4">
          <p className="text-sm text-slate-700">
            검색 결과 <span className="font-bold" style={{color: '#97C1A9'}}>{filteredCourses.length}</span>개
          </p>
        </div>

        {/* Course Grid - 2 columns */}
        {filteredCourses.length === 0 ? (
          <div className="bg-white rounded-lg p-12 text-center border" style={{borderColor: '#B6CFB6'}}>
            <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-700 mb-1">검색 결과가 없습니다</h3>
            <p className="text-sm text-slate-500">다른 검색어를 시도해보세요</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredCourses.map((course) => (
              <div 
                key={course.id} 
                className="bg-white rounded-lg border hover:shadow-lg transition-all duration-200"
                style={{borderColor: '#B6CFB6'}}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = '#8FCACA'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = '#B6CFB6'}
              >
                {/* Header */}
                <div className="p-4 border-b" style={{borderColor: '#CCE2CB'}}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="text-base font-bold text-slate-900 mb-1">{course.name}</h3>
                      <p className="text-sm text-slate-600">{course.professor}</p>
                      <p className="text-xs text-slate-500 mt-1">{course.department} • {course.credits}학점</p>
                    </div>
                    <div className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg border" style={{backgroundColor: '#FFF9E6', borderColor: '#FFD700'}}>
                      <Star className="w-4 h-4 text-amber-500 fill-current" />
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
                          className="px-2 py-0.5 text-xs rounded border"
                          style={{backgroundColor: '#D4F0F0', color: '#2C5F5F', borderColor: '#8FCACA'}}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Summary */}
                  {course.aiSummary && (
                    <div className="rounded-lg p-3 mb-3 border" style={{backgroundColor: '#D4F0F0', borderColor: '#8FCACA'}}>
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
                    <div className="text-center p-2 rounded border" style={{backgroundColor: '#CCE2CB', borderColor: '#B6CFB6'}}>
                      <div className="text-xs text-slate-600 mb-1">난이도</div>
                      <div className="text-xs font-semibold text-slate-800">
                        {course.difficulty || 3}/5
                      </div>
                    </div>
                    <div className="text-center p-2 rounded border" style={{backgroundColor: '#CCE2CB', borderColor: '#B6CFB6'}}>
                      <div className="text-xs text-slate-600 mb-1">과제량</div>
                      <div className="text-xs font-semibold text-slate-800">
                        {course.workload || 3}/5
                      </div>
                    </div>
                    <div className="text-center p-2 rounded border" style={{backgroundColor: '#CCE2CB', borderColor: '#B6CFB6'}}>
                      <div className="text-xs text-slate-600 mb-1">학점</div>
                      <div className="text-xs font-semibold text-slate-800">
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
                    className="w-full py-2 text-white rounded-lg transition-all font-medium text-sm shadow-sm"
                    style={{background: 'linear-gradient(to right, #8FCACA, #97C1A9)'}}
                    onMouseEnter={(e) => e.target.style.background = 'linear-gradient(to right, #7AB8B8, #86B098)'}
                    onMouseLeave={(e) => e.target.style.background = 'linear-gradient(to right, #8FCACA, #97C1A9)'}
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
          <div className="bg-white rounded-lg p-12 text-center border" style={{borderColor: '#B6CFB6'}}>
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
