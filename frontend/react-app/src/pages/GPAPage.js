import React, { useState } from 'react';
import { Minus, Plus, Target, Calculator } from 'lucide-react';

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
    <div className="h-[calc(100vh-200px)] flex flex-col">
      {/* GPA Header */}
      <div className="bg-white border-b border-slate-200 p-4 rounded-t-xl">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-sky-100 rounded-lg">
            <Calculator className="w-6 h-6 text-sky-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-800">학점 계산</h2>
            <p className="text-sm text-slate-500">궁금한 강의 정보를 자연어로 물어보세요</p>
          </div>
        </div>
      </div>

      {/* Current Status */}
      <div className="bg-white border-b border-slate-200 p-4">
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center p-3 bg-sky-50 rounded-lg border border-sky-100">
            <div className="text-xl font-bold text-sky-600">{mockUserProfile.gpa}</div>
            <div className="text-xs text-slate-600">현재 학점</div>
          </div>
          <div className="text-center p-3 bg-sky-50 rounded-lg border border-sky-100">
            <div className="text-xl font-bold text-sky-600">{calculateGPA()}</div>
            <div className="text-xs text-slate-600">예상 학점</div>
          </div>
          <div className="text-center p-3 bg-slate-50 rounded-lg border border-slate-200">
            <div className="text-xl font-bold text-slate-700">{mockUserProfile.totalCredits}</div>
            <div className="text-xs text-slate-600">이수 학점</div>
          </div>
          <div className="text-center p-3 bg-slate-50 rounded-lg border border-slate-200">
            <div className="text-xl font-bold text-slate-700">0.55</div>
            <div className="text-xs text-slate-600">목표까지</div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 bg-slate-50 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          {/* GPA Calculator */}
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">학점 계산기</h3>
            
            <div className="space-y-2 mb-4">
              {selectedCourses.map((course, index) => (
                <div key={index} className="flex items-center gap-2 p-2 border border-slate-200 rounded-lg">
                  <input
                    type="text"
                    value={course.name}
                    className="flex-1 px-2 py-1 text-sm border-0 focus:outline-none bg-transparent"
                    placeholder="강의명"
                    readOnly
                  />
                  <select 
                    value={course.credits}
                    className="px-2 py-1 text-xs border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-sky-400"
                  >
                    <option value={1}>1학점</option>
                    <option value={2}>2학점</option>
                    <option value={3}>3학점</option>
                  </select>
                  <select
                    value={course.grade}
                    className="px-2 py-1 text-xs border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-sky-400"
                  >
                    <option value="A+">A+</option>
                    <option value="A0">A0</option>
                    <option value="B+">B+</option>
                    <option value="B0">B0</option>
                    <option value="C+">C+</option>
                    <option value="C0">C0</option>
                  </select>
                  <button className="p-1 text-red-500 hover:bg-red-50 rounded transition-colors">
                    <Minus className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>

            <button className="w-full py-2 border border-dashed border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600 mb-3 text-sm transition-colors">
              <Plus className="w-4 h-4 inline mr-1" />
              강의 추가
            </button>

            <div className="bg-sky-50 rounded-lg p-3 border border-sky-100">
              <div className="flex justify-between items-center">
                <span className="font-medium text-slate-800">예상 평균 학점</span>
                <span className="text-lg font-bold text-sky-600">{calculateGPA()}</span>
              </div>
              <div className="text-sm text-slate-600 mt-1">
                총 {selectedCourses.reduce((sum, course) => sum + course.credits, 0)}학점
              </div>
            </div>
          </div>

          {/* Retake Recommendations */}
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">재수강 추천</h3>
            
            <div className="space-y-2 mb-4">
              {[
                { name: '자료구조', currentGrade: 'C+', credits: 3, impact: '+0.23' },
                { name: '알고리즘', currentGrade: 'B0', credits: 3, impact: '+0.15' },
                { name: '운영체제', currentGrade: 'C0', credits: 3, impact: '+0.31' }
              ].map((course, index) => (
                <div key={index} className="flex items-center justify-between p-2 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
                  <div>
                    <h4 className="font-medium text-slate-800 text-sm">{course.name}</h4>
                    <p className="text-xs text-slate-600">현재: {course.currentGrade} ({course.credits}학점)</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-sky-600 text-sm">{course.impact}</p>
                    <p className="text-xs text-slate-500">학점 상승</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
              <h4 className="font-medium text-slate-800 mb-1">재수강 전략</h4>
              <ul className="text-sm text-slate-700 space-y-1">
                <li>• C학점 과목 우선 재수강 권장</li>
                <li>• 목표 학점 4.0 달성까지 2학기 소요</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Graduation Requirements */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <h3 className="font-semibold text-slate-800 mb-3">졸업 요건 분석</h3>
          
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <h4 className="font-medium text-slate-800 mb-2">전공 필수</h4>
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">이수 학점</span>
                  <span className="font-semibold text-slate-800">24/30</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div className="bg-sky-600 h-2 rounded-full" style={{width: '80%'}}></div>
                </div>
                <div className="text-xs text-slate-500">6학점 부족</div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-slate-800 mb-2">전공 선택</h4>
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">이수 학점</span>
                  <span className="font-semibold text-slate-800">36/42</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div className="bg-slate-600 h-2 rounded-full" style={{width: '86%'}}></div>
                </div>
                <div className="text-xs text-slate-500">6학점 부족</div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-slate-800 mb-2">교양</h4>
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">이수 학점</span>
                  <span className="font-semibold text-slate-800">38/38</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div className="bg-slate-600 h-2 rounded-full" style={{width: '100%'}}></div>
                </div>
                <div className="text-xs text-slate-600">완료</div>
              </div>
            </div>
          </div>

          <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
            <h4 className="font-medium text-slate-800 mb-2">졸업까지 로드맵</h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="font-medium mb-1 text-slate-800">다음 학기 권장</p>
                <ul className="text-slate-700 space-y-1">
                  <li>• 컴퓨터네트워크 (전필, 3학점)</li>
                  <li>• 모바일프로그래밍 (전선, 3학점)</li>
                </ul>
              </div>
              <div>
                <p className="font-medium mb-1 text-slate-800">최종 학기 권장</p>
                <ul className="text-slate-700 space-y-1">
                  <li>• 인공지능 (전선, 3학점)</li>
                  <li>• 클라우드컴퓨팅 (전선, 3학점)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* GPA Prediction */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <h3 className="font-semibold text-slate-800 mb-3">학점 변화 예측</h3>
          <div className="h-32 bg-slate-50 rounded-lg flex items-center justify-center border border-slate-200">
            <div className="text-center text-slate-500">
              <div className="p-2 bg-sky-100 rounded-full inline-block mb-2">
                <Target className="w-6 h-6 text-sky-600" />
              </div>
              <p className="font-medium">학점 변화 그래프</p>
              <p className="text-sm">현재 3.45 → 목표 4.0</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GPAPage;