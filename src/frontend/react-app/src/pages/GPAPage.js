import React, { useState } from 'react';
import { Minus, Plus, Target } from 'lucide-react';

const GPAPage = ({ mockUserProfile }) => {
  const [selectedCourses] = useState([
    { name: '웹프로그래밍', credits: 3, grade: 'A+', gradePoint: 4.5 },
    { name: '데이터베이스', credits: 3, grade: 'B+', gradePoint: 3.5 }
  ]);

  const calculateGPA = () => {
    const totalPoints = selectedCourses.reduce((sum, course) => sum + (course.credits * course.gradePoint), 0);
    const totalCredits = selectedCourses.reduce((sum, course) => sum + course.credits, 0);
    return totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : '0.00';
  };

  return (
    <div className="space-y-6">
      {/* Current Status */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 border border-green-100">
        <div className="grid grid-cols-4 gap-6">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">현재 학점</p>
            <p className="text-3xl font-bold text-green-600">{mockUserProfile.gpa}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">예상 학점</p>
            <p className="text-3xl font-bold text-blue-600">{calculateGPA()}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">이수 학점</p>
            <p className="text-3xl font-bold text-purple-600">{mockUserProfile.totalCredits}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">목표까지</p>
            <p className="text-3xl font-bold text-orange-600">0.55</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* GPA Calculator */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-bold mb-4">학점 계산기</h3>
          
          <div className="space-y-3 mb-4">
            {selectedCourses.map((course, index) => (
              <div key={index} className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg">
                <input
                  type="text"
                  value={course.name}
                  className="flex-1 px-2 py-1 text-sm border-0 focus:outline-none"
                  placeholder="강의명"
                />
                <select 
                  value={course.credits}
                  className="px-2 py-1 text-sm border border-gray-200 rounded"
                >
                  <option value={1}>1학점</option>
                  <option value={2}>2학점</option>
                  <option value={3}>3학점</option>
                </select>
                <select
                  value={course.grade}
                  className="px-2 py-1 text-sm border border-gray-200 rounded"
                >
                  <option value="A+">A+</option>
                  <option value="A0">A0</option>
                  <option value="B+">B+</option>
                  <option value="B0">B0</option>
                  <option value="C+">C+</option>
                  <option value="C0">C0</option>
                </select>
                <button className="p-1 text-red-500 hover:bg-red-50 rounded">
                  <Minus className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          <button className="w-full py-2 border border-dashed border-gray-300 rounded-lg hover:bg-gray-50 text-gray-600 mb-4">
            <Plus className="w-4 h-4 inline mr-1" />
            강의 추가
          </button>

          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold">예상 평균 학점</span>
              <span className="text-xl font-bold text-blue-600">{calculateGPA()}</span>
            </div>
            <div className="text-sm text-gray-600">
              총 {selectedCourses.reduce((sum, course) => sum + course.credits, 0)}학점
            </div>
          </div>
        </div>

        {/* Retake Recommendations */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-bold mb-4">재수강 추천</h3>
          
          <div className="space-y-3 mb-4">
            {[
              { name: '자료구조', currentGrade: 'C+', credits: 3, impact: '+0.23' },
              { name: '알고리즘', currentGrade: 'B0', credits: 3, impact: '+0.15' },
              { name: '운영체제', currentGrade: 'C0', credits: 3, impact: '+0.31' }
            ].map((course, index) => (
              <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-semibold">{course.name}</h4>
                  <p className="text-sm text-gray-600">현재: {course.currentGrade} ({course.credits}학점)</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-green-600">{course.impact}</p>
                  <p className="text-xs text-gray-500">학점 상승 예상</p>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-orange-50 rounded-lg p-4">
            <h4 className="font-semibold text-orange-800 mb-2">💡 재수강 전략</h4>
            <ul className="text-sm text-orange-700 space-y-1">
              <li>• C학점 과목 우선 재수강 권장</li>
              <li>• 3학점 과목이 학점 상승에 더 효과적</li>
              <li>• 목표 학점 4.0 달성까지 2학기 소요 예상</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Graduation Requirements */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold mb-4">졸업 요건 분석</h3>
        
        <div className="grid grid-cols-3 gap-6">
          <div>
            <h4 className="font-semibold mb-3">전공 필수</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">이수 학점</span>
                <span className="font-semibold">24/30</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{width: '80%'}}></div>
              </div>
              <div className="text-xs text-gray-500">6학점 부족</div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3">전공 선택</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">이수 학점</span>
                <span className="font-semibold">36/42</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{width: '86%'}}></div>
              </div>
              <div className="text-xs text-gray-500">6학점 부족</div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3">교양</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">이수 학점</span>
                <span className="font-semibold">38/38</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{width: '100%'}}></div>
              </div>
              <div className="text-xs text-green-600">완료</div>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-semibold text-blue-800 mb-2">📋 졸업까지 로드맵</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="font-semibold mb-1">다음 학기 권장 과목</p>
              <ul className="text-blue-700 space-y-1">
                <li>• 컴퓨터네트워크 (전필, 3학점)</li>
                <li>• 모바일프로그래밍 (전선, 3학점)</li>
                <li>• 캡스톤디자인 (전필, 3학점)</li>
              </ul>
            </div>
            <div>
              <p className="font-semibold mb-1">최종 학기 권장 과목</p>
              <ul className="text-blue-700 space-y-1">
                <li>• 인공지능 (전선, 3학점)</li>
                <li>• 클라우드컴퓨팅 (전선, 3학점)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* GPA Prediction Chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold mb-4">학점 변화 예측</h3>
        <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
          <div className="text-center text-gray-500">
            <Target className="w-12 h-12 mx-auto mb-2" />
            <p>학점 변화 그래프</p>
            <p className="text-sm">현재 3.45 → 목표 4.0</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GPAPage;
