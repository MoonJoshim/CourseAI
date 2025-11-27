import React, { useEffect, useState } from 'react';
import {
  Star, User, BookOpen, GraduationCap, Clock, Calendar, MapPin, Award
} from 'lucide-react';

const resolveApiBaseUrl = () => {
  const envBase = (process.env.REACT_APP_BACKEND_URL || '').trim().replace(/\/$/, '');

  if (typeof window === 'undefined') {
    return envBase;
  }

  const isSecurePage = window.location.protocol === 'https:';

  if (envBase) {
    const isEnvSecure = envBase.startsWith('https://');
    const isEnvRelative = envBase.startsWith('/');

    if (isEnvSecure || !isSecurePage || isEnvRelative) {
      return envBase;
    }

    if (envBase.startsWith('http://') && isSecurePage) {
      return '';
    }
  }

  return '';
};

const buildApiPath = (path = '') => {
  const base = resolveApiBaseUrl();
  if (!path.startsWith('/')) {
    path = `/${path}`;
  }
  return base ? `${base}${path}` : path;
};

const DetailPage = ({ selectedCourse, mockCourses }) => {
  const course = selectedCourse || mockCourses[0];
  const [reviewSummary, setReviewSummary] = useState({
    text: null,
    isLoading: false,
    error: null,
  });

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    const fetchReviewSummary = async () => {
      if (!course?.name) {
        if (isMounted) {
          setReviewSummary({
            text: null,
            isLoading: false,
            error: null,
          });
        }
        return;
      }

      setReviewSummary((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      try {
        // 강의평 요약 API 호출
        const apiUrl = buildApiPath(`/api/reviews/summary`);
        const params = new URLSearchParams({
          course_name: course.name,
        });
        
        if (course.professor) {
          params.append('professor', course.professor);
        }

        const fullUrl = `${apiUrl}?${params.toString()}`;
        console.log('📝 Fetching review summary from:', fullUrl);
        console.log('📋 Course info:', { name: course.name, professor: course.professor });

        const response = await fetch(fullUrl, {
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
          },
        });

        if (!response.ok) {
          const errorText = await response.text().catch(() => '');
          console.error('❌ API Error:', response.status, errorText);
          throw new Error(`강의평 요약을 불러오지 못했습니다. (${response.status})`);
        }

        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
          const text = await response.text();
          console.error('❌ Non-JSON response:', text.substring(0, 200));
          if (text.trim().startsWith('<!')) {
            throw new Error('서버 설정 오류: API 엔드포인트를 찾을 수 없습니다.');
          }
          throw new Error('예상하지 못한 응답 형식입니다.');
        }

        const data = await response.json();
        console.log('✅ Summary API Response:', { 
          success: data.success, 
          reviewCount: data.review_count,
          hasSummary: !!data.summary,
          summaryLength: data.summary?.length || 0
        });
        
        if (!isMounted) {
          return;
        }

        if (!data.success) {
          console.error('❌ API returned success=false:', data.error);
          // API 실패 시에도 기본 요약이 있으면 표시
          setReviewSummary({
            text: null,
            isLoading: false,
            error: data.error || '강의평 요약을 생성하는 중 오류가 발생했습니다.',
          });
          return;
        }

        // 요약이 있으면 표시, 없으면 에러로 처리하지 않고 기본 요약 사용
        setReviewSummary({
          text: data.summary || null,
          isLoading: false,
          error: null,
        });
      } catch (error) {
        if (error.name === 'AbortError') {
          return;
        }

        console.error('❌ Error fetching review summary:', error);
        
        if (isMounted) {
          setReviewSummary({
            text: null,
            isLoading: false,
            error: error.message || '강의평 요약을 불러오는 중 오류가 발생했습니다.',
          });
        }
      }
    };

    fetchReviewSummary();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [course?.name, course?.professor]);

  
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-6xl mx-auto px-6 py-5">
        {/* Course Header */}
        <div className="bg-white rounded-lg border border-slate-200 p-6 mb-4">
          <div className="flex justify-between items-start mb-6">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-slate-900 mb-2">{course.name}</h1>
              {course.courseCode && (
                <p className="text-sm text-slate-600 mb-3">과목코드: {course.courseCode}</p>
              )}
              
              <div className="grid grid-cols-2 gap-3 mt-4">
                <div className="flex items-center gap-2 text-sm text-slate-700">
                  <User className="w-4 h-4 text-slate-400" />
                  <span><span className="text-xs text-slate-500">담당교수</span> {course.professor}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-700">
                  <BookOpen className="w-4 h-4 text-slate-400" />
                  <span><span className="text-xs text-slate-500">개설학과</span> {course.department}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-700">
                  <GraduationCap className="w-4 h-4 text-slate-400" />
                  <span><span className="text-xs text-slate-500">학점</span> {course.credits}학점</span>
                </div>
                {course.timeSlot && course.timeSlot !== '-' && (
                  <div className="flex items-center gap-2 text-sm text-slate-700">
                    <Clock className="w-4 h-4 text-slate-400" />
                    <span><span className="text-xs text-slate-500">시간</span> {course.timeSlot}</span>
                  </div>
                )}
                {course.room && course.room !== '-' && (
                  <div className="flex items-center gap-2 text-sm text-slate-700">
                    <MapPin className="w-4 h-4 text-slate-400" />
                    <span><span className="text-xs text-slate-500">강의실</span> {course.room}</span>
                  </div>
                )}
                {course.semester && (
                  <div className="flex items-center gap-2 text-sm text-slate-700">
                    <Calendar className="w-4 h-4 text-slate-400" />
                    <span><span className="text-xs text-slate-500">학기</span> {course.semester}</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="text-center">
              <div className="flex items-center gap-2 mb-2 bg-amber-50 px-5 py-4 rounded-lg border border-amber-200">
                <Star className="w-7 h-7 text-amber-500 fill-current" />
                <div>
                  <div className="text-3xl font-bold text-slate-900">{course.rating}</div>
                  <div className="text-xs text-slate-500">/ 5.0</div>
                </div>
              </div>
              <div className="flex items-center gap-1 justify-center text-sm text-slate-600 mt-2">
                <Award className="w-4 h-4" />
                <span>{course.reviewCount}개 리뷰</span>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-5 gap-3 pt-5 border-t border-slate-200">
            <div className="text-center p-3 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-600 mb-1">평점</p>
              <p className="text-lg font-bold text-slate-900">{course.rating}</p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-600 mb-1">만족도</p>
              <p className="text-lg font-bold text-slate-900">{course.sentiment}%</p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-600 mb-1">난이도</p>
              <p className="text-lg font-bold text-slate-900">{course.difficulty}/5</p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-600 mb-1">과제량</p>
              <p className="text-lg font-bold text-slate-900">{course.workload}/5</p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-600 mb-1">학점</p>
              <p className="text-lg font-bold text-slate-900">{course.gradeGenerosity}/5</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {/* Reviews Summary */}
          <div className="col-span-2 space-y-4">
            {/* 수강생 평가 요약 */}
            <div className="bg-white rounded-lg border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-bold text-slate-900">수강생 평가 요약</h3>
                {reviewSummary.isLoading && (
                  <span className="text-xs text-slate-500">요약 생성 중...</span>
                )}
              </div>

              {reviewSummary.error && (
                <div className="mb-3 p-3 bg-rose-50 border border-rose-200 rounded-lg">
                  <p className="text-xs text-rose-600 font-medium mb-1">⚠️ 강의평 요약을 불러오는 중 오류가 발생했습니다</p>
                  <p className="text-xs text-rose-500">{reviewSummary.error}</p>
                  <p className="text-xs text-rose-400 mt-1">브라우저 콘솔(F12)에서 자세한 정보를 확인할 수 있습니다.</p>
                </div>
              )}

              {reviewSummary.text ? (
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">{reviewSummary.text}</p>
                </div>
              ) : reviewSummary.isLoading ? (
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <p className="text-sm text-slate-500">요약을 생성하는 중입니다...</p>
                </div>
              ) : reviewSummary.error ? (
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <p className="text-sm text-slate-500 mb-2">요약 생성 중 오류가 발생했습니다.</p>
                  {course.aiSummary && (
                    <div className="mt-3 pt-3 border-t border-slate-200">
                      <p className="text-xs text-slate-500 mb-2">기본 요약 정보:</p>
                      <p className="text-sm text-slate-700 leading-relaxed">{course.aiSummary}</p>
                    </div>
                  )}
                </div>
              ) : course.aiSummary ? (
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <p className="text-sm text-slate-700 leading-relaxed">{course.aiSummary}</p>
                </div>
              ) : (
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <p className="text-sm text-slate-500">강의평 데이터가 없어 요약을 생성할 수 없습니다.</p>
                </div>
              )}
            </div>
          </div>

          {/* Tags & Info */}
          <div className="space-y-4">
            {/* Tags */}
            {course.tags && course.tags.length > 0 && (
              <div className="bg-white rounded-lg border border-slate-200 p-5">
                <h3 className="text-base font-bold text-slate-900 mb-3">강의 특징</h3>
                <div className="flex flex-wrap gap-2">
                  {course.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-full border border-slate-200 text-sm"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Additional Info */}
            <div className="bg-white rounded-lg border border-slate-200 p-5">
              <h3 className="text-base font-bold text-slate-900 mb-3">상세 정보</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between py-2 border-b border-slate-100">
                  <span className="text-slate-600">인기도</span>
                  <span className="font-semibold text-slate-900">{course.popularity || 0}점</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-100">
                  <span className="text-slate-600">추세</span>
                  <span className="font-semibold text-slate-900">{course.trend === 'up' ? '↑ 상승' : course.trend === 'down' ? '↓ 하락' : '-'}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-slate-600">총 리뷰</span>
                  <span className="font-semibold text-slate-900">{course.reviewCount}개</span>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default DetailPage;
