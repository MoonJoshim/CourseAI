import React from 'react';
import { User, Lightbulb, Calendar, Users, Star, Award } from 'lucide-react';

const RecommendPage = ({ mockUserProfile, mockCourses }) => {
  return (
    <div className="h-[calc(100vh-200px)] flex flex-col">
      {/* Recommend Header */}
      <div className="bg-white border-b border-slate-200 p-4 rounded-t-xl">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-sky-100 rounded-lg">
            <Award className="w-6 h-6 text-sky-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-800">맞춤 추천</h2>
            <p className="text-sm text-slate-500">궁금한 강의 정보를 자연어로 물어보세요</p>
          </div>
        </div>
      </div>

      {/* User Profile Summary */}
      <div className="bg-white border-b border-slate-200 p-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-sky-500 rounded-full flex items-center justify-center">
            <User className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-slate-800">{mockUserProfile.name}</h3>
            <p className="text-sm text-slate-600">{mockUserProfile.major} • {mockUserProfile.semester}학기</p>
          </div>
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-xs text-slate-500">학점</p>
              <p className="font-bold text-sky-600">{mockUserProfile.gpa}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">이수</p>
              <p className="font-bold text-emerald-600">{mockUserProfile.totalCredits}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">남은</p>
              <p className="font-bold text-orange-600">{mockUserProfile.requiredCredits - mockUserProfile.totalCredits}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">진행률</p>
              <p className="font-bold text-purple-600">{Math.round((mockUserProfile.totalCredits / mockUserProfile.requiredCredits) * 100)}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 bg-slate-50 space-y-4">
        {/* Personalized Recommendations */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <div className="flex items-center gap-2 mb-3">
            <div className="p-2 bg-sky-100 rounded-lg">
              <Lightbulb className="w-4 h-4 text-sky-600" />
            </div>
            <h3 className="font-semibold text-slate-800">AI 맞춤 추천</h3>
            <span className="bg-sky-600 text-white text-xs px-2 py-1 rounded font-medium">개인화</span>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            {mockCourses.slice(0, 2).map(course => (
              <div key={course.id} className="border border-slate-200 rounded-lg p-3 hover:border-sky-200 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-medium text-slate-800">{course.name}</h4>
                    <p className="text-sm text-slate-600">{course.professor} • {course.credits}학점</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 text-amber-400 fill-current" />
                    <span className="font-semibold text-slate-800">{course.rating}</span>
                  </div>
                </div>
                
                <div className="bg-amber-50 rounded-lg p-2 mb-2 border border-amber-100">
                  <p className="text-xs text-amber-800">
                    <strong>추천 이유:</strong> {mockUserProfile.preferences.join(', ')} 영역과 관련
                  </p>
                </div>

                <div className="flex gap-1">
                  {course.tags.slice(0, 3).map((tag, index) => (
                    <span key={index} className="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded border border-slate-200">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <button className="w-full py-2 border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600 transition-colors text-sm">
            더 많은 추천 강의 보기
          </button>
        </div>

        {/* Schedule Recommendation */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <div className="flex items-center gap-2 mb-3">
            <div className="p-2 bg-sky-100 rounded-lg">
              <Calendar className="w-4 h-4 text-sky-600" />
            </div>
            <h3 className="font-semibold text-slate-800">스마트 시간표</h3>
          </div>

          <div className="grid grid-cols-7 gap-1 mb-3">
            <div className="text-center text-xs font-medium p-2"></div>
            {['월', '화', '수', '목', '금'].map(day => (
              <div key={day} className="text-center text-xs font-medium p-2 text-slate-600">{day}</div>
            ))}
            <div></div>

            {[1, 2, 3, 4, 5, 6].map(period => (
              <React.Fragment key={period}>
                <div className="text-center text-xs p-2 text-slate-600">{period}교시</div>
                {['월', '화', '수', '목', '금'].map(day => (
                  <div key={`${day}-${period}`} className="p-1 border border-slate-200 min-h-8 rounded text-center">
                    {(period === 1 && day === '월') && (
                      <div className="bg-sky-100 text-sky-800 text-xs p-1 rounded">
                        소프트웨어공학
                      </div>
                    )}
                    {(period === 3 && day === '수') && (
                      <div className="bg-emerald-100 text-emerald-800 text-xs p-1 rounded">
                        웹프로그래밍
                      </div>
                    )}
                  </div>
                ))}
                <div></div>
              </React.Fragment>
            ))}
          </div>

          <div className="bg-sky-50 rounded-lg p-3 border border-sky-100">
            <h4 className="font-medium text-sky-800 mb-1">추천 분석</h4>
            <ul className="text-sm text-sky-700 space-y-1">
              <li>• 전공필수 2과목, 전공선택 1과목으로 균형잡힌 구성</li>
              <li>• 오전 시간대 위주로 배치하여 효율적인 학습 가능</li>
            </ul>
          </div>
        </div>

        {/* Similar Students */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <div className="flex items-center gap-2 mb-3">
            <div className="p-2 bg-emerald-100 rounded-lg">
              <Users className="w-4 h-4 text-emerald-600" />
            </div>
            <h3 className="font-semibold text-slate-800">비슷한 학생들의 선택</h3>
          </div>

          <div className="space-y-2">
            {mockCourses.map(course => (
              <div key={course.id} className="flex items-center justify-between p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
                <div>
                  <h4 className="font-medium text-slate-800">{course.name}</h4>
                  <p className="text-sm text-slate-600">{course.professor} • {course.department}</p>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 mb-1">
                    <Star className="w-4 h-4 text-amber-400 fill-current" />
                    <span className="font-semibold text-slate-800">{course.rating}</span>
                  </div>
                  <p className="text-xs text-slate-500">{course.reviewCount}명 수강</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecommendPage;