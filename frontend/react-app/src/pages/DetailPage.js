import React from 'react';
import { 
  Star, User, BookOpen, GraduationCap, Clock
} from 'lucide-react';

const DetailPage = ({ selectedCourse, mockCourses }) => {
  const course = selectedCourse || mockCourses[0];
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/20 to-slate-50">
      <div className="max-w-6xl mx-auto px-6 py-5">
        {/* Course Header */}
        <div className="bg-gradient-to-br from-white to-slate-50/50 rounded-lg border border-slate-200 p-6 mb-4">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-slate-900">{course.name}</h1>
                {course.courseCode && (
                  <span className="text-base text-slate-500">({course.courseCode})</span>
                )}
              </div>
              <div className="flex items-center gap-4 text-sm text-slate-600 mb-2">
                <span className="flex items-center gap-1">
                  <User className="w-4 h-4" />
                  {course.professor}
                </span>
                <span className="flex items-center gap-1">
                  <BookOpen className="w-4 h-4" />
                  {course.department}
                </span>
                <span className="flex items-center gap-1">
                  <GraduationCap className="w-4 h-4" />
                  {course.credits}학점
                </span>
                {course.timeSlot && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {course.timeSlot}
                  </span>
                )}
              </div>
              {course.room && course.semester && (
                <p className="text-sm text-slate-500">{course.room} • {course.semester}</p>
              )}
            </div>
            
            <div className="text-right">
              <div className="flex items-center gap-2 mb-2 bg-amber-50 px-4 py-3 rounded-lg border border-amber-200">
                <Star className="w-6 h-6 text-amber-500 fill-current" />
                <span className="text-3xl font-bold text-slate-900">{course.rating}</span>
                <span className="text-slate-500">/ 5.0</span>
              </div>
              <p className="text-sm text-slate-600">{course.reviewCount}개의 강의평</p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-5 gap-3 pt-4 border-t border-slate-200">
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-xs text-slate-600 mb-1">전체 평점</p>
              <p className="text-lg font-bold text-slate-900">{course.rating}</p>
            </div>
            <div className="text-center p-3 bg-gradient-to-br from-blue-50 to-slate-50 rounded-lg border border-blue-200">
              <p className="text-xs text-slate-600 mb-1">만족도</p>
              <p className="text-lg font-bold text-blue-600">{course.sentiment}%</p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-xs text-slate-600 mb-1">난이도</p>
              <p className="text-lg font-bold text-slate-700">{course.difficulty}/5</p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-xs text-slate-600 mb-1">과제량</p>
              <p className="text-lg font-bold text-slate-700">{course.workload}/5</p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-xs text-slate-600 mb-1">성적</p>
              <p className="text-lg font-bold text-slate-700">{course.gradeGenerosity}/5</p>
            </div>
          </div>
        </div>

        {/* AI Summary */}
        {course.aiSummary && (
          <div className="bg-gradient-to-br from-white to-slate-50/50 rounded-lg border border-slate-200 p-6 mb-4">
            <h3 className="text-base font-bold text-slate-900 mb-3">수강생 평가 요약</h3>
            <div className="bg-gradient-to-br from-blue-50 to-slate-50 rounded-lg p-4 border border-blue-200">
              <p className="text-sm text-slate-700 leading-relaxed">{course.aiSummary}</p>
            </div>
          </div>
        )}

        {/* Tags */}
        {course.tags && course.tags.length > 0 && (
          <div className="bg-gradient-to-br from-white to-slate-50/50 rounded-lg border border-slate-200 p-6">
            <h3 className="text-base font-bold text-slate-900 mb-3">강의 특징</h3>
            <div className="flex flex-wrap gap-2">
              {course.tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full border border-blue-200 text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DetailPage;
