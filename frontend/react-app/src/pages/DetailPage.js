import React, { useEffect, useMemo, useState } from 'react';
import {
  Star, User, BookOpen, GraduationCap, Clock, Calendar, MapPin, Award
} from 'lucide-react';

const MAX_DYNAMIC_REVIEWS = 12;

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

const sortReviewsByRecency = (reviews = []) =>
  [...reviews].sort((a = {}, b = {}) => {
    const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
    const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
    if (dateA !== dateB) {
      return dateB - dateA;
    }
    return (b.semester || '').localeCompare(a.semester || '');
  });

const DetailPage = ({ selectedCourse, mockCourses }) => {
  const course = selectedCourse || mockCourses[0];
  const [remoteReviews, setRemoteReviews] = useState({
    items: [],
    total: null,
    isLoading: false,
    error: null,
  });

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    const fetchReviews = async () => {
      if (!course?.name) {
        if (isMounted) {
          setRemoteReviews({
            items: [],
            total: null,
            isLoading: false,
            error: null,
          });
        }
        return;
      }

      setRemoteReviews((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      try {
        // Pinecone에서 직접 강의평 가져오기
        const apiUrl = buildApiPath(`/api/reviews/from-pinecone`);
        const params = new URLSearchParams({
          course_name: course.name,
          limit: '100',
        });
        
        if (course.professor) {
          params.append('professor', course.professor);
        }

        const fullUrl = `${apiUrl}?${params.toString()}`;
        console.log('🔍 Fetching reviews from:', fullUrl);
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
          throw new Error(`강의평을 불러오지 못했습니다. (${response.status})`);
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
        console.log('✅ API Response:', { success: data.success, total: data.total, reviewsCount: data.reviews?.length });
        
        if (!data.success) {
          console.error('❌ API returned success=false:', data.error);
          throw new Error(data.error || '강의평을 불러오는 중 오류가 발생했습니다.');
        }

        const matchedReviews = Array.isArray(data.reviews) ? sortReviewsByRecency(data.reviews) : [];
        console.log(`✅ Found ${matchedReviews.length} reviews after sorting`);

        if (!isMounted) {
          return;
        }

        setRemoteReviews({
          items: matchedReviews,
          total: data.total ?? matchedReviews.length,
          isLoading: false,
          error: null,
        });
      } catch (error) {
        if (error.name === 'AbortError') {
          return;
        }

        console.error('❌ Error fetching reviews:', error);
        
        if (isMounted) {
          setRemoteReviews({
            items: [],
            total: null,
            isLoading: false,
            error: error.message || '강의평을 불러오는 중 오류가 발생했습니다.',
          });
        }
      }
    };

    fetchReviews();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [course?.name, course?.professor]);

  const fallbackGeneratedReviews = useMemo(() => {
    const summary = course?.aiSummary || '';
    const sentences = summary
      .split(/(?<=[.!?])\s+/)
      .map((sentence) => sentence.trim())
      .filter(Boolean);

    const baseSentences = sentences.length > 0 ? sentences : ['강의평 데이터가 준비 중입니다.'];
    const fallbackCount = Math.min(
      Math.max(course?.reviewCount || baseSentences.length, 2),
      5
    );

    return Array.from({ length: fallbackCount }, (_, index) => baseSentences[index % baseSentences.length]);
  }, [course?.aiSummary, course?.reviewCount]);

  const hasRemoteReviews = remoteReviews.items.length > 0;
  const displayedRemoteReviews = hasRemoteReviews
    ? remoteReviews.items.slice(0, MAX_DYNAMIC_REVIEWS)
    : [];
  const reviewCountLabel = hasRemoteReviews
    ? remoteReviews.total ?? displayedRemoteReviews.length
    : course.reviewCount || fallbackGeneratedReviews.length;
  const fallbackRatingLabel =
    typeof course?.rating === 'number' ? course.rating.toFixed(1) : course?.rating || '4.5';
  const fallbackSemesterLabel = course?.semester || '최근 학기';
  
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
          {/* Reviews */}
          <div className="col-span-2 space-y-4">
            {/* AI Summary */}
            {course.aiSummary && (
              <div className="bg-white rounded-lg border border-slate-200 p-6">
                <h3 className="text-base font-bold text-slate-900 mb-4">수강생 평가 요약</h3>
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">{course.aiSummary}</p>
                </div>
              </div>
            )}

            <div className="bg-white rounded-lg border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-bold text-slate-900">강의평 ({reviewCountLabel})</h3>
                {remoteReviews.isLoading && (
                  <span className="text-xs text-slate-500">불러오는 중...</span>
                )}
              </div>

              {remoteReviews.error && (
                <div className="mb-3 p-3 bg-rose-50 border border-rose-200 rounded-lg">
                  <p className="text-xs text-rose-600 font-medium mb-1">⚠️ 강의평을 불러오는 중 오류가 발생했습니다</p>
                  <p className="text-xs text-rose-500">{remoteReviews.error}</p>
                  <p className="text-xs text-rose-400 mt-1">브라우저 콘솔(F12)에서 자세한 정보를 확인할 수 있습니다.</p>
                </div>
              )}

              {hasRemoteReviews ? (
                <div className="space-y-3">
                  {displayedRemoteReviews.map((review, index) => (
                    <div
                      key={review.review_id || `${review.semester || 'review'}-${index}`}
                      className="p-4 bg-slate-50 rounded-lg border border-slate-200"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        {typeof review.rating === 'number' && review.rating > 0 && (
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4 text-amber-500 fill-current" />
                            <span className="font-bold text-slate-900">
                              {review.rating.toFixed(1)}
                            </span>
                          </div>
                        )}
                        {review.semester && (
                          <span className="text-xs text-slate-500">• {review.semester}</span>
                        )}
                        {review.source && (
                          <span className="text-xs text-slate-400 uppercase tracking-wide">
                            {review.source}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-slate-700 leading-relaxed">
                        {review.comment || review.text || '강의평 내용이 없습니다.'}
                      </p>
                    </div>
                  ))}
                  {remoteReviews.total && remoteReviews.total > displayedRemoteReviews.length && (
                    <p className="text-xs text-slate-500 text-right">
                      총 {remoteReviews.total}개 중 {displayedRemoteReviews.length}개만 표시 중
                    </p>
                  )}
                </div>
              ) : (
                <div className="space-y-3">
                  {remoteReviews.error ? (
                    <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                      <p className="text-sm text-amber-800 font-medium mb-2">
                        ⚠️ 실제 강의평 데이터를 불러오지 못했습니다
                      </p>
                      <p className="text-xs text-amber-700 mb-3">
                        API 서버 연결에 실패하여 요약 정보를 표시합니다. 
                        브라우저 콘솔(F12)에서 자세한 오류를 확인할 수 있습니다.
                      </p>
                      <p className="text-xs text-amber-600">
                        실제 강의평 데이터는 서버가 정상 작동할 때 자동으로 표시됩니다.
                      </p>
                    </div>
                  ) : null}
                  {fallbackGeneratedReviews.map((text, idx) => (
                    <div
                      key={`fallback-${idx}`}
                      className="p-4 bg-slate-50 rounded-lg border border-slate-200"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 text-amber-500 fill-current" />
                          <span className="font-bold text-slate-900">{fallbackRatingLabel}</span>
                        </div>
                        <span className="text-xs text-slate-500">• {fallbackSemesterLabel}</span>
                        <span className="text-xs text-slate-400 bg-slate-200 px-2 py-0.5 rounded">
                          요약
                        </span>
                      </div>
                      <p className="text-sm text-slate-700 leading-relaxed">
                        {text || '강의평 데이터가 준비 중입니다.'}
                      </p>
                    </div>
                  ))}
                  {!remoteReviews.error && remoteReviews.total === 0 && (
                    <p className="text-xs text-slate-500">등록된 강의평이 아직 없습니다.</p>
                  )}
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
