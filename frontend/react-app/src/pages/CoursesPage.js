import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Search, Filter, Grid, List, BookOpen, User, Clock, Star, GraduationCap } from 'lucide-react';
import softwareCourses from '../data/softwareCourses.json';

const STATIC_COURSES = softwareCourses;
const PAGE_SIZE = 50;

const CoursesPage = () => {
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [selectedProfessor, setSelectedProfessor] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('course_name');
  const [showFilters, setShowFilters] = useState(false);

  const loadMoreRef = useRef(null);
  const offsetRef = useRef(0);
  const searchQueryRef = useRef('');
  const hasMoreRef = useRef(true);

  const fetchCourses = useCallback(({ reset = false, query } = {}) => {
    const normalizedTerm = typeof query === 'string' ? query.trim() : searchQueryRef.current;

    if (!reset && !hasMoreRef.current) {
      return;
    }

    if (reset) {
      searchQueryRef.current = normalizedTerm;
      offsetRef.current = 0;
      setLoading(true);
      setCourses([]);
      setFilteredCourses([]);
      setHasMore(true);
      hasMoreRef.current = true;
    } else {
      setLoadingMore(true);
    }

    const currentOffset = reset ? 0 : offsetRef.current;
    const keywordLower = normalizedTerm.toLowerCase();

    const matchesKeyword = (course) => {
      if (!keywordLower) {
        return true;
      }

      const tokens = [
        course.course_name,
        course.professor,
        course.department,
        course.major,
        course.course_code,
        course.course_english_name,
        course.lecture_time,
      ];

      if (Array.isArray(course.tags)) {
        tokens.push(...course.tags);
      }
      if (Array.isArray(course.keywords)) {
        tokens.push(...course.keywords);
      }

      return tokens.some((value) => (value || '').toString().toLowerCase().includes(keywordLower));
    };

    const filteredAll = STATIC_COURSES.filter(matchesKeyword);
    const nextSlice = filteredAll.slice(currentOffset, currentOffset + PAGE_SIZE);

    const applyResults = () => {
      if (reset) {
        setCourses(nextSlice);
        setFilteredCourses(nextSlice);
      } else if (nextSlice.length > 0) {
        setCourses((prev) => [...prev, ...nextSlice]);
        setFilteredCourses((prev) => [...prev, ...nextSlice]);
      }

      const newOffset = currentOffset + nextSlice.length;
      offsetRef.current = newOffset;

      const total = filteredAll.length;
      setTotalCount(total);

      const nextHasMore = newOffset < total;
      setHasMore(nextHasMore);
      hasMoreRef.current = nextHasMore;

      if (reset && nextSlice.length === 0) {
        setHasMore(false);
        hasMoreRef.current = false;
      }

      setLoading(false);
      setLoadingMore(false);
    };

    // 비동기 흐름을 흉내 내기 위해 다음 틱에 상태 업데이트
    if (typeof window !== 'undefined' && typeof window.requestAnimationFrame === 'function') {
      window.requestAnimationFrame(applyResults);
    } else {
      setTimeout(applyResults, 0);
    }
  }, []);

  // 초기 로딩
  useEffect(() => {
    fetchCourses({ reset: true, query: '' });
  }, [fetchCourses]);

  // 검색어 변경 시 새로운 검색 실행
  useEffect(() => {
    const normalizedTerm = searchTerm.trim();

    if (normalizedTerm === searchQueryRef.current) {
      return () => {};
    }

    const timeoutId = setTimeout(() => {
      fetchCourses({ reset: true, query: normalizedTerm });
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [fetchCourses, searchTerm]);

  // 필터링 (클라이언트 사이드)
  useEffect(() => {
    let filtered = [...courses];

    // 학과 필터링
    if (selectedDepartment) {
      filtered = filtered.filter(course => course.department === selectedDepartment);
    }

    // 교수 필터링
    if (selectedProfessor) {
      filtered = filtered.filter(course => course.professor === selectedProfessor);
    }

    // 정렬
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'course_name':
          return a.course_name.localeCompare(b.course_name);
        case 'professor':
          return a.professor.localeCompare(b.professor);
        case 'department':
          return a.department.localeCompare(b.department);
        case 'credits':
          return b.credits - a.credits;
        default:
          return 0;
      }
    });

    setFilteredCourses(filtered);
  }, [courses, selectedDepartment, selectedProfessor, sortBy]);

  // 고유 학과 목록 추출
  const departments = [...new Set(courses.map(course => course.department))].sort();
  
  // 고유 교수 목록 추출
  const professors = [...new Set(courses.map(course => course.professor))].sort();

  // 무한 스크롤 처리
  useEffect(() => {
    const target = loadMoreRef.current;
    if (!target) return;

    const observer = new IntersectionObserver((entries) => {
      const entry = entries[0];
      if (entry.isIntersecting && hasMore && !loading && !loadingMore) {
        fetchCourses();
      }
    }, {
      root: null,
      rootMargin: '200px',
      threshold: 0
    });

    observer.observe(target);
    return () => observer.disconnect();
  }, [fetchCourses, hasMore, loading, loadingMore]);

  const CourseCard = ({ course }) => (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6 border border-gray-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{course.course_name}</h3>
          <p className="text-sm text-gray-600 mb-1">{course.course_english_name}</p>
          <p className="text-sm text-blue-600 font-medium">{course.course_code}</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
            {course.credits}학점
          </span>
          <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
            {course.hours}시간
          </span>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-gray-600">
          <User className="w-4 h-4 mr-2" />
          <span>{course.professor}</span>
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <GraduationCap className="w-4 h-4 mr-2" />
          <span>{course.department}</span>
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <Clock className="w-4 h-4 mr-2" />
          <span>{course.lecture_time || '시간 미정'}</span>
        </div>
        {course.target_grade && (
          <div className="flex items-center text-sm text-gray-600">
            <BookOpen className="w-4 h-4 mr-2" />
            <span>{course.target_grade}</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <span className="bg-gray-100 px-2 py-1 rounded">
            {course.lecture_method}
          </span>
          <span className="bg-gray-100 px-2 py-1 rounded">
            {course.class_type}
          </span>
        </div>
        <div className="flex items-center text-sm text-gray-500">
          <Star className="w-4 h-4 mr-1" />
          <span>{course.average_rating || 0.0}</span>
          <span className="ml-1">({course.total_reviews || 0})</span>
        </div>
      </div>
    </div>
  );

  const CourseListItem = ({ course }) => (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 p-4 border border-gray-200">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-4 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{course.course_name}</h3>
            <span className="text-sm text-blue-600 font-medium">{course.course_code}</span>
            <div className="flex space-x-2">
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                {course.credits}학점
              </span>
              <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                {course.hours}시간
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-6 text-sm text-gray-600">
            <div className="flex items-center">
              <User className="w-4 h-4 mr-1" />
              <span>{course.professor}</span>
            </div>
            <div className="flex items-center">
              <GraduationCap className="w-4 h-4 mr-1" />
              <span>{course.department}</span>
            </div>
            <div className="flex items-center">
              <Clock className="w-4 h-4 mr-1" />
              <span>{course.lecture_time || '시간 미정'}</span>
            </div>
            <div className="flex items-center">
              <Star className="w-4 h-4 mr-1" />
              <span>{course.average_rating || 0.0} ({course.total_reviews || 0})</span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <span className="bg-gray-100 px-2 py-1 rounded">{course.lecture_method}</span>
          <span className="bg-gray-100 px-2 py-1 rounded">{course.class_type}</span>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">개설과목 현황</h1>
            <p className="text-gray-600 mt-1">2025-2학기 개설된 모든 과목을 확인하세요</p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 검색 및 필터 */}
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="과목명, 교수명, 학과명으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Filter className="w-4 h-4" />
              <span>필터</span>
            </button>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">학과</label>
                <select
                  value={selectedDepartment}
                  onChange={(e) => setSelectedDepartment(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">전체 학과</option>
                  {departments.map(dept => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">교수</label>
                <select
                  value={selectedProfessor}
                  onChange={(e) => setSelectedProfessor(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">전체 교수</option>
                  {professors.map(prof => (
                    <option key={prof} value={prof}>{prof}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">정렬</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="course_name">과목명</option>
                  <option value="professor">교수명</option>
                  <option value="department">학과</option>
                  <option value="credits">학점</option>
                </select>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 결과 통계 */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {searchTerm ? (
              <>
                '<span className="font-semibold">{searchTerm}</span>' 검색 결과: 
                <span className="font-semibold text-blue-600 ml-1">{filteredCourses.length}</span>개
                {totalCount > 0 && (
                  <span className="text-gray-500 ml-2">(전체 {totalCount}개 중)</span>
                )}
              </>
            ) : (
              <>
                표시된 과목: <span className="font-semibold text-blue-600">{filteredCourses.length}</span>개
                {totalCount > 0 && (
                  <span className="text-gray-500 ml-2">(전체 {totalCount}개 중)</span>
                )}
                {hasMore && (
                  <span className="text-green-600 ml-2">• 스크롤하여 더 보기</span>
                )}
              </>
            )}
          </div>
          <div className="text-sm text-gray-500">
            {viewMode === 'grid' ? '그리드 보기' : '리스트 보기'}
          </div>
        </div>
      </div>

      {/* 강의 목록 */}
      {filteredCourses.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">검색 결과가 없습니다</h3>
          <p className="text-gray-500">다른 검색어나 필터를 시도해보세요.</p>
        </div>
      ) : (
        <div className={viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
          : 'space-y-4'
        }>
          {filteredCourses.map((course) => (
            viewMode === 'grid' ? (
              <CourseCard key={course.course_id} course={course} />
            ) : (
              <CourseListItem key={course.course_id} course={course} />
            )
          ))}
        </div>
      )}

      <div ref={loadMoreRef} className="h-1" aria-hidden="true"></div>

      {/* 더 로딩 인디케이터 */}
      {loadingMore && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">더 많은 강의를 불러오는 중...</span>
        </div>
      )}

      {/* 더 이상 로드할 데이터가 없을 때 */}
      {!loading && !loadingMore && !hasMore && filteredCourses.length > 0 && (
        <div className="text-center py-8 text-gray-500">
          <BookOpen className="w-8 h-8 mx-auto mb-2" />
          <p>모든 강의를 불러왔습니다.</p>
        </div>
      )}
    </div>
  );
};

export default CoursesPage;

