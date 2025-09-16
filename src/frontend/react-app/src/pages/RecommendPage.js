import React from 'react';
import { User, Lightbulb, Calendar, Users, Star } from 'lucide-react';

const RecommendPage = ({ mockUserProfile, mockCourses }) => {
  return (
    <div className="space-y-6">
      {/* User Profile Card */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold">{mockUserProfile.name}님을 위한 추천</h2>
            <p className="text-gray-600">{mockUserProfile.major} • {mockUserProfile.semester}학기</p>
          </div>
        </div>
        
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-sm text-gray-600">현재 학점</p>
            <p className="text-xl font-bold text-blue-600">{mockUserProfile.gpa}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">이수 학점</p>
            <p className="text-xl font-bold text-green-600">{mockUserProfile.totalCredits}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">남은 학점</p>
            <p className="text-xl font-bold text-orange-600">{mockUserProfile.requiredCredits - mockUserProfile.totalCredits}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">진행률</p>
            <p className="text-xl font-bold text-purple-600">{Math.round((mockUserProfile.totalCredits / mockUserProfile.requiredCredits) * 100)}%</p>
          </div>
        </div>
      </div>

      {/* Personalized Recommendations */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb className="w-5 h-5 text-yellow-500" />
          <h3 className="text-lg font-bold">맞춤 강의 추천</h3>
          <span className="bg-gradient-to-r from-yellow-100 to-orange-100 text-orange-800 text-xs px-2 py-1 rounded">
            AI 추천
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          {mockCourses.slice(0, 2).map(course => (
            <div key={course.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-bold">{course.name}</h4>
                  <p className="text-sm text-gray-600">{course.professor} • {course.credits}학점</p>
                </div>
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                  <span className="font-semibold">{course.rating}</span>
                </div>
              </div>
              
              <div className="bg-yellow-50 rounded-lg p-3 mb-3">
                <p className="text-sm text-yellow-800 mb-1">
                  <strong>추천 이유:</strong>
                </p>
                <p className="text-xs text-yellow-700">
                  회원님이 선호하는 '{mockUserProfile.preferences.join(', ')}' 영역과 관련된 강의입니다.
                </p>
              </div>

              <div className="flex gap-2">
                {course.tags.slice(0, 3).map((tag, index) => (
                  <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <button className="w-full py-3 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600">
          더 많은 추천 강의 보기
        </button>
      </div>

      {/* Schedule Recommendation */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-5 h-5 text-blue-500" />
          <h3 className="text-lg font-bold">스마트 시간표 추천</h3>
        </div>

        <div className="grid grid-cols-7 gap-2 mb-4">
          <div className="text-center text-sm font-semibold p-2"></div>
          {['월', '화', '수', '목', '금'].map(day => (
            <div key={day} className="text-center text-sm font-semibold p-2">{day}</div>
          ))}
          <div></div>

          {[1, 2, 3, 4, 5, 6].map(period => (
            <React.Fragment key={period}>
              <div className="text-center text-sm p-2 border-r">{period}교시</div>
              {['월', '화', '수', '목', '금'].map(day => (
                <div key={`${day}-${period}`} className="p-2 border border-gray-200 min-h-12">
                  {(period === 1 && day === '월') && (
                    <div className="bg-blue-100 text-blue-800 text-xs p-1 rounded">
                      소프트웨어공학
                    </div>
                  )}
                  {(period === 3 && day === '수') && (
                    <div className="bg-green-100 text-green-800 text-xs p-1 rounded">
                      웹프로그래밍
                    </div>
                  )}
                </div>
              ))}
              <div></div>
            </React.Fragment>
          ))}
        </div>

        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="font-semibold mb-2">💡 추천 시간표 분석</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• 전공필수 2과목, 전공선택 1과목으로 균형잡힌 구성</li>
            <li>• 오전 시간대 위주로 배치하여 효율적인 학습 가능</li>
            <li>• 졸업요건 중 전공 12학점 충족</li>
          </ul>
        </div>
      </div>

      {/* Similar Students */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-5 h-5 text-green-500" />
          <h3 className="text-lg font-bold">비슷한 학생들이 선택한 강의</h3>
        </div>

        <div className="space-y-3">
          {mockCourses.map(course => (
            <div key={course.id} className="flex items-center justify-between p-3 border border-gray-100 rounded-lg hover:bg-gray-50">
              <div>
                <h4 className="font-semibold">{course.name}</h4>
                <p className="text-sm text-gray-600">{course.professor} • {course.department}</p>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 mb-1">
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                  <span className="font-semibold">{course.rating}</span>
                </div>
                <p className="text-xs text-gray-500">{course.reviewCount}명이 수강</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RecommendPage;
