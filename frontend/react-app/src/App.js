import React, { useState } from 'react';
import NavBar from './components/NavBar';
import SearchPage from './pages/SearchPage';
import DetailPage from './pages/DetailPage';
import ChatPage from './pages/ChatPage';
import GPAPage from './pages/GPAPage';
import MyPage from './pages/MyPage';
import CoursesPage from './pages/CoursesPage';
import AuthForm from './components/AuthForm';
import { useAuth } from './context/AuthContext';

const AICoursePlatform = () => {
  const [currentPage, setCurrentPage] = useState('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('rating');
  const { user, loading: authLoading, isAuthenticating, authError } = useAuth();

  // Mock data
  const mockCourses = [
    {
      id: 1,
      courseCode: 'CS301',
      name: '소프트웨어공학',
      professor: '김교수',
      department: '소프트웨어학과',
      credits: 3,
      rating: 4.5,
      reviewCount: 127,
      popularity: 89,
      tags: ['노팀플', '적당한과제', '출석중요', '성적잘줌'],
      semester: '2024-2',
      timeSlot: '월(1,2) 수(3)',
      room: '공학관 301호',
      aiSummary:
        '팀플 없고 과제 적당한 편. 출석은 중요하지만 성적은 잘 주는 편입니다.',
      sentiment: 85,
      difficulty: 3,
      workload: 2,
      gradeGenerosity: 4,
      bookmarked: false,
      trend: 'up',
      keywords: ['객체지향', '설계패턴', '프로젝트관리', 'UML'],
    },
    {
      id: 2,
      courseCode: 'CS302',
      name: '데이터베이스',
      professor: '이교수',
      department: '컴퓨터공학과',
      credits: 3,
      rating: 3.8,
      reviewCount: 89,
      popularity: 67,
      tags: ['팀플있음', '과제많음', '실습위주'],
      semester: '2024-2',
      timeSlot: '화(1,2) 목(3)',
      room: '공학관 205호',
      aiSummary: '실습 위주의 수업. 팀플과 과제가 많지만 실력 향상에 도움됩니다.',
      sentiment: 72,
      difficulty: 4,
      workload: 4,
      gradeGenerosity: 3,
      bookmarked: true,
      trend: 'down',
      keywords: ['SQL', 'NoSQL', '정규화', '트랜잭션'],
    },
    {
      id: 3,
      courseCode: 'CS303',
      name: '웹프로그래밍',
      professor: '박교수',
      department: '소프트웨어학과',
      credits: 3,
      rating: 4.2,
      reviewCount: 156,
      popularity: 95,
      tags: ['재밌음', '실용적', '포트폴리오도움'],
      semester: '2024-2',
      timeSlot: '월(3,4) 금(1,2)',
      room: '공학관 401호',
      aiSummary:
        '재미있고 실용적인 수업. 포트폴리오 만들기에 도움되는 강의입니다.',
      sentiment: 92,
      difficulty: 3,
      workload: 3,
      gradeGenerosity: 4,
      bookmarked: false,
      trend: 'up',
      keywords: ['React', 'Node.js', 'API', '프론트엔드'],
    },
  ];

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'search':
        return (
          <SearchPage
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            viewMode={viewMode}
            setViewMode={setViewMode}
            sortBy={sortBy}
            setSortBy={setSortBy}
            mockCourses={mockCourses}
            setSelectedCourse={setSelectedCourse}
            setCurrentPage={setCurrentPage}
          />
        );
      case 'chat':
        return <ChatPage />;
      case 'detail':
        return (
          <DetailPage
            selectedCourse={selectedCourse}
            mockCourses={mockCourses}
          />
        );
      case 'gpa':
        return <GPAPage />;
      case 'mypage':
        return <MyPage />;
      case 'courses':
        return <CoursesPage />;
      default:
        return (
          <SearchPage
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            viewMode={viewMode}
            setViewMode={setViewMode}
            sortBy={sortBy}
            setSortBy={setSortBy}
            mockCourses={mockCourses}
            setSelectedCourse={setSelectedCourse}
            setCurrentPage={setCurrentPage}
          />
        );
    }
  };

  if (authLoading || isAuthenticating) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-600">
        로그인 상태를 확인하고 있습니다...
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-sky-50 to-white flex flex-col items-center justify-center px-6">
        <div className="max-w-md w-full bg-white border border-slate-200 rounded-2xl shadow-lg p-8 space-y-6">
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-semibold text-slate-900">CourseAI</h1>
            <p className="text-sm text-slate-600">
              소프트웨어학과 강의 분석 서비스를 이용하려면 먼저 회원가입 또는 로그인을 해주세요.
            </p>
          </div>
          <AuthForm />
          {authError && (
            <p className="text-xs text-rose-500 text-center">{authError}</p>
          )}
          <p className="text-xs text-slate-400 text-center">
            이메일과 비밀번호만으로 간단하게 가입할 수 있습니다.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <div className="max-w-7xl mx-auto px-6 py-8">{renderCurrentPage()}</div>
    </div>
  );
};

export default AICoursePlatform;

