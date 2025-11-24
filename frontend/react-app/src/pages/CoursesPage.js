import React, { useState, useEffect, useMemo } from 'react';
import { Search, Grid, List, BookOpen, User, Clock, Star, GraduationCap, Filter } from 'lucide-react';
import softwareCourses from '../data/softwareCourses.json';

const REQUIRED_COURSES = [
  '컴퓨터네트워크',
  '데이터베이스',
  '인공지능입문',
  '디지털회로',
  '객체지향프로그래밍및실습',
  '컴퓨터프로그래밍및실습'
];

const CoursesPage = () => {
  const [activeTab, setActiveTab] = useState('required'); // required, elective, general
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('course_name');

  // 과목 분류
  const categorizedCourses = useMemo(() => {
    const required = [];
    const elective = [];
    
    softwareCourses.forEach(course => {
      if (REQUIRED_COURSES.includes(course.course_name)) {
        required.push(course);
      } else {
        elective.push(course);
      }
    });

    return { required, elective, general: [] };
  }, []);

  // 현재 탭의 과목들
  const currentCourses = useMemo(() => {
    let courses = [];
    switch (activeTab) {
      case 'required':
        courses = categorizedCourses.required;
        break;
      case 'elective':
        courses = categorizedCourses.elective;
        break;
      case 'general':
        courses = categorizedCourses.general;
        break;
      default:
        courses = [];
    }
    return courses;
  }, [activeTab, categorizedCourses]);

  // 필터링 및 정렬
  const filteredCourses = useMemo(() => {
    let filtered = [...currentCourses];

    // 검색어 필터
    if (searchTerm.trim()) {
      const query = searchTerm.toLowerCase();
      filtered = filtered.filter(course =>
        course.course_name.toLowerCase().includes(query) ||
        course.professor.toLowerCase().includes(query) ||
        course.course_code.toLowerCase().includes(query) ||
        (course.course_english_name && course.course_english_name.toLowerCase().includes(query))
      );
    }

    // 학과 필터
    if (selectedDepartment) {
      filtered = filtered.filter(course => course.department === selectedDepartment);
    }

    // 정렬
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'course_name':
          return a.course_name.localeCompare(b.course_name);
        case 'professor':
          return a.professor.localeCompare(b.professor);
        case 'credits':
          return b.credits - a.credits;
        default:
          return 0;
      }
    });

    return filtered;
  }, [currentCourses, searchTerm, selectedDepartment, sortBy]);

  // 고유 학과 목록
  const departments = useMemo(() => {
    const depts = new Set(currentCourses.map(course => course.department));
    return ['', ...Array.from(depts).sort()];
  }, [currentCourses]);

  const CourseCard = ({ course }) => (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 p-5 border border-slate-200">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-slate-900 mb-1">{course.course_name}</h3>
          <p className="text-sm text-slate-600 mb-1">{course.course_english_name}</p>
          <p className="text-sm text-sky-600 font-medium">{course.course_code}</p>
        </div>
        <div className="flex gap-2">
          <span className="bg-blue-50 text-blue-700 text-xs px-2.5 py-1 rounded-full font-medium border border-blue-200">
            {course.credits}학점
          </span>
          <span className="bg-green-50 text-green-700 text-xs px-2.5 py-1 rounded-full font-medium border border-green-200">
            {course.hours}시간
          </span>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-slate-700">
          <User className="w-4 h-4 mr-2 text-slate-400" />
          <span className="font-medium">{course.professor}</span>
        </div>
        <div className="flex items-center text-sm text-slate-600">
          <GraduationCap className="w-4 h-4 mr-2 text-slate-400" />
          <span>{course.department}</span>
        </div>
        {course.lecture_time && (
          <div className="flex items-center text-sm text-slate-600">
            <Clock className="w-4 h-4 mr-2 text-slate-400" />
            <span className="truncate">{course.lecture_time}</span>
          </div>
        )}
        {course.target_grade && (
          <div className="flex items-center text-sm text-slate-600">
            <BookOpen className="w-4 h-4 mr-2 text-slate-400" />
            <span>{course.target_grade}</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-slate-100">
        <div className="flex gap-2">
          {course.lecture_method && (
            <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs">
              {course.lecture_method}
            </span>
          )}
          {course.class_type && (
            <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs">
              {course.class_type}
            </span>
          )}
        </div>
        <div className="flex items-center text-sm text-slate-500">
          <Star className="w-4 h-4 mr-1 text-amber-400 fill-current" />
          <span className="font-medium">{course.average_rating || 0.0}</span>
          <span className="ml-1 text-xs">({course.total_reviews || 0})</span>
        </div>
      </div>
    </div>
  );

  const CourseListItem = ({ course }) => (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 p-4 border border-slate-200">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-4 mb-2">
            <h3 className="text-lg font-bold text-slate-900">{course.course_name}</h3>
            <span className="text-sm text-sky-600 font-medium">{course.course_code}</span>
            <div className="flex gap-2">
              <span className="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded-full font-medium">
                {course.credits}학점
              </span>
              <span className="bg-green-50 text-green-700 text-xs px-2 py-1 rounded-full font-medium">
                {course.hours}시간
              </span>
            </div>
          </div>
          <div className="flex items-center gap-6 text-sm text-slate-600">
            <div className="flex items-center">
              <User className="w-4 h-4 mr-1 text-slate-400" />
              <span>{course.professor}</span>
            </div>
            <div className="flex items-center">
              <GraduationCap className="w-4 h-4 mr-1 text-slate-400" />
              <span>{course.department}</span>
            </div>
            {course.lecture_time && (
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1 text-slate-400" />
                <span>{course.lecture_time}</span>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex gap-2">
            {course.lecture_method && (
              <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs">
                {course.lecture_method}
              </span>
            )}
            {course.class_type && (
              <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs">
                {course.class_type}
              </span>
            )}
          </div>
          <div className="flex items-center">
            <Star className="w-4 h-4 mr-1 text-amber-400 fill-current" />
            <span className="font-medium">{course.average_rating || 0.0}</span>
            <span className="ml-1 text-xs text-slate-500">({course.total_reviews || 0})</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">📖 개설과목 현황</h1>
            <p className="text-slate-600">2025-2학기 소프트웨어학과 개설과목을 확인하세요</p>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => setActiveTab('required')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === 'required'
                  ? 'bg-gradient-to-r from-sky-600 to-blue-600 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
              }`}
            >
              전공필수 ({categorizedCourses.required.length})
            </button>
            <button
              onClick={() => setActiveTab('elective')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === 'elective'
                  ? 'bg-gradient-to-r from-sky-600 to-blue-600 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
              }`}
            >
              전공선택 ({categorizedCourses.elective.length})
            </button>
            <button
              onClick={() => setActiveTab('general')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === 'general'
                  ? 'bg-gradient-to-r from-sky-600 to-blue-600 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
              }`}
            >
              교양선택 (0)
            </button>
          </div>

          {/* Search and Filters */}
          <div className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="과목명, 교수명, 과목코드로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
              />
            </div>

            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 bg-white"
            >
              <option value="">전체 학과</option>
              {departments.map(dept => dept && (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 bg-white"
            >
              <option value="course_name">과목명순</option>
              <option value="professor">교수명순</option>
              <option value="credits">학점순</option>
            </select>

            <div className="flex gap-2 bg-slate-100 p-1 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === 'grid' ? 'bg-white text-sky-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <Grid className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === 'list' ? 'bg-white text-sky-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Results Info */}
        <div className="mb-4 flex items-center justify-between bg-white rounded-lg px-4 py-3 shadow-sm border border-slate-200">
          <div className="text-sm text-slate-600">
            {searchTerm ? (
              <>
                '<span className="font-semibold text-slate-900">{searchTerm}</span>' 검색 결과: 
                <span className="font-bold text-sky-600 ml-1">{filteredCourses.length}</span>개
              </>
            ) : (
              <>
                총 <span className="font-bold text-sky-600">{filteredCourses.length}</span>개 과목
              </>
            )}
          </div>
          <div className="text-sm text-slate-500">
            {viewMode === 'grid' ? '카드 보기' : '목록 보기'}
          </div>
        </div>

        {/* Course List */}
        {activeTab === 'general' ? (
          <div className="bg-white rounded-xl p-16 text-center shadow-sm">
            <BookOpen className="w-20 h-20 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-700 mb-2">교양선택 과목</h3>
            <p className="text-slate-500">곧 업데이트 예정입니다</p>
          </div>
        ) : filteredCourses.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center shadow-sm">
            <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-700 mb-2">검색 결과가 없습니다</h3>
            <p className="text-slate-500">다른 검색어나 필터를 시도해보세요</p>
          </div>
        ) : (
          <div className={
            viewMode === 'grid' 
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' 
              : 'space-y-3'
          }>
            {filteredCourses.map((course) => (
              viewMode === 'grid' ? (
                <CourseCard key={`${course.course_id}-${course.professor}`} course={course} />
              ) : (
                <CourseListItem key={`${course.course_id}-${course.professor}`} course={course} />
              )
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CoursesPage;
