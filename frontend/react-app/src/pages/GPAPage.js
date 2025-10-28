import React, { useState } from 'react';
import { Minus, Plus, Target, Calculator } from 'lucide-react';

const GPAPage = ({ mockUserProfile }) => {
  const [selectedCourses, setSelectedCourses] = useState([
    { name: '웹프로그래밍', credits: 3, grade: 'A+', gradePoint: 4.5 },
    { name: '데이터베이스', credits: 3, grade: 'B+', gradePoint: 3.5 }
  ]);

  // 등급별 점수 매핑 (4.5 만점 기준)
  const gradeToPoint = {
    'A+': 4.5,
    'A0': 4.0,
    'B+': 3.5,
    'B0': 3.0,
    'C+': 2.5,
    'C0': 2.0,
    'D+': 1.5,
    'D0': 1.0,
    'F': 0.0
  };

  // 등급 선택 옵션
  const gradeOptions = Object.keys(gradeToPoint);

  // 학점 계산 함수 (가중평균)
  const calculateGPA = () => {
    const totalPoints = selectedCourses.reduce((sum, course) => {
      const gradePoint = gradeToPoint[course.grade] || 0;
      return sum + (course.credits * gradePoint);
    }, 0);
    
    const totalCredits = selectedCourses.reduce((sum, course) => sum + course.credits, 0);
    
    return totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : '0.00';
  };

  // 강의 추가 함수
  const addCourse = () => {
    const newCourse = {
      name: '',
      credits: 3,
      grade: 'A+',
      gradePoint: 4.5
    };
    setSelectedCourses([...selectedCourses, newCourse]);
  };

  // 강의 제거 함수
  const removeCourse = (index) => {
    if (selectedCourses.length > 1) {
      setSelectedCourses(selectedCourses.filter((_, i) => i !== index));
    }
  };

  // 강의 정보 업데이트 함수
  const updateCourse = (index, field, value) => {
    const updatedCourses = selectedCourses.map((course, i) => {
      if (i === index) {
        const updated = { ...course, [field]: value };
        if (field === 'grade') {
          updated.gradePoint = gradeToPoint[value] || 0;
        }
        return updated;
      }
      return course;
    });
    setSelectedCourses(updatedCourses);
  };

  // 재수강 추천 계산 함수
  const calculateRetakeRecommendations = () => {
    const currentGPA = parseFloat(calculateGPA());
    const targetGPA = 4.0;
    
    // 현재 성적이 낮은 과목들을 찾아서 재수강 시 학점 상승 효과 계산
    const retakeCandidates = selectedCourses
      .filter(course => gradeToPoint[course.grade] < 4.0)
      .map(course => {
        const currentPoint = gradeToPoint[course.grade];
        const potentialPoint = 4.5; // A+로 재수강한다고 가정
        const impact = ((potentialPoint - currentPoint) * course.credits) / selectedCourses.reduce((sum, c) => sum + c.credits, 0);
        
        return {
          name: course.name,
          currentGrade: course.grade,
          credits: course.credits,
          impact: `+${impact.toFixed(2)}`,
          impactValue: impact,
          type: 'retake'
        };
      })
      .sort((a, b) => b.impactValue - a.impactValue)
      .slice(0, 3); // 상위 3개만 추천

    return retakeCandidates;
  };

  // 유사 과목 추천 함수
  const getSimilarCourseRecommendations = () => {
    // C학점을 받은 과목들 찾기
    const cGradeCourses = selectedCourses.filter(course => 
      course.grade === 'C+' || course.grade === 'C0' || course.grade === 'D+' || course.grade === 'D0' || course.grade === 'F'
    );

    // 과목명 기반으로 유사한 과목 추천 (실제로는 AI나 데이터베이스에서 가져와야 함)
    const similarCourses = [];
    
    cGradeCourses.forEach(course => {
      const courseName = course.name.toLowerCase();
      
      // 과목명 패턴 매칭으로 유사 과목 추천
      if (courseName.includes('프로그래밍') || courseName.includes('programming')) {
        similarCourses.push({
          name: '고급프로그래밍',
          department: '컴퓨터공학과',
          credits: course.credits,
          reason: '프로그래밍 기초 강화',
          difficulty: '중급',
          type: 'similar'
        });
        similarCourses.push({
          name: '소프트웨어공학',
          department: '컴퓨터공학과',
          credits: course.credits,
          reason: '프로그래밍 설계 방법론',
          difficulty: '중급',
          type: 'similar'
        });
      }
      
      if (courseName.includes('데이터') || courseName.includes('data')) {
        similarCourses.push({
          name: '데이터마이닝',
          department: '컴퓨터공학과',
          credits: course.credits,
          reason: '데이터 분석 심화',
          difficulty: '고급',
          type: 'similar'
        });
        similarCourses.push({
          name: '빅데이터처리',
          department: '컴퓨터공학과',
          credits: course.credits,
          reason: '대용량 데이터 처리',
          difficulty: '고급',
          type: 'similar'
        });
      }
      
      if (courseName.includes('수학') || courseName.includes('math')) {
        similarCourses.push({
          name: '이산수학',
          department: '수학과',
          credits: course.credits,
          reason: '컴퓨터과학 기초 수학',
          difficulty: '중급',
          type: 'similar'
        });
        similarCourses.push({
          name: '확률통계',
          department: '수학과',
          credits: course.credits,
          reason: '통계적 사고력 향상',
          difficulty: '중급',
          type: 'similar'
        });
      }
      
      if (courseName.includes('네트워크') || courseName.includes('network')) {
        similarCourses.push({
          name: '네트워크보안',
          department: '컴퓨터공학과',
          credits: course.credits,
          reason: '네트워크 보안 심화',
          difficulty: '고급',
          type: 'similar'
        });
        similarCourses.push({
          name: '클라우드컴퓨팅',
          department: '컴퓨터공학과',
          credits: course.credits,
          reason: '분산 시스템 이해',
          difficulty: '고급',
          type: 'similar'
        });
      }
    });

    // 중복 제거 및 상위 3개만 반환
    const uniqueCourses = similarCourses.filter((course, index, self) => 
      index === self.findIndex(c => c.name === course.name)
    ).slice(0, 3);

    return uniqueCourses;
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
            <div className="text-xs text-slate-600">희망 학점</div>
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
                    onChange={(e) => updateCourse(index, 'name', e.target.value)}
                    className="flex-1 px-2 py-1 text-sm border-0 focus:outline-none bg-transparent"
                    placeholder="강의명"
                  />
                  <select 
                    value={course.credits}
                    onChange={(e) => updateCourse(index, 'credits', parseInt(e.target.value))}
                    className="px-2 py-1 text-xs border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-sky-400"
                  >
                    <option value={1}>1학점</option>
                    <option value={2}>2학점</option>
                    <option value={3}>3학점</option>
                    <option value={4}>4학점</option>
                  </select>
                  <select
                    value={course.grade}
                    onChange={(e) => updateCourse(index, 'grade', e.target.value)}
                    className="px-2 py-1 text-xs border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-sky-400"
                  >
                    {gradeOptions.map(grade => (
                      <option key={grade} value={grade}>{grade}</option>
                    ))}
                  </select>
                  <button 
                    onClick={() => removeCourse(index)}
                    className="p-1 text-red-500 hover:bg-red-50 rounded transition-colors"
                    disabled={selectedCourses.length <= 1}
                  >
                    <Minus className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>

            <button 
              onClick={addCourse}
              className="w-full py-2 border border-dashed border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600 mb-3 text-sm transition-colors"
            >
              <Plus className="w-4 h-4 inline mr-1" />
              강의 추가
            </button>

            <div className="bg-sky-50 rounded-lg p-3 border border-sky-100">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium text-slate-800">희망 평균 학점</span>
                <span className="text-lg font-bold text-sky-600">{calculateGPA()}/4.5</span>
              </div>
              <div className="text-sm text-slate-600 space-y-1">
                <div>총 {selectedCourses.reduce((sum, course) => sum + course.credits, 0)}학점</div>
                <div className="text-xs text-slate-500">
                  가중평균: {selectedCourses.reduce((sum, course) => sum + (course.credits * (gradeToPoint[course.grade] || 0)), 0).toFixed(1)}점 / {selectedCourses.reduce((sum, course) => sum + course.credits, 0)}학점
                </div>
              </div>
            </div>
          </div>

          {/* Retake Recommendations */}
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">재수강 추천</h3>
            
            {/* 재수강 과목 */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-slate-700 mb-2">재수강 과목</h4>
              <div className="space-y-2">
                {calculateRetakeRecommendations().length > 0 ? (
                  calculateRetakeRecommendations().map((course, index) => (
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
                  ))
                ) : (
                  <div className="text-center py-2 text-slate-500">
                    <p className="text-xs">재수강 추천 과목이 없습니다</p>
                  </div>
                )}
              </div>
            </div>

            {/* 유사 과목 추천 */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-slate-700 mb-2">유사 과목 추천</h4>
              <div className="space-y-2">
                {getSimilarCourseRecommendations().length > 0 ? (
                  getSimilarCourseRecommendations().map((course, index) => (
                    <div key={index} className="flex items-center justify-between p-2 border border-green-200 rounded-lg hover:bg-green-50 transition-colors">
                      <div>
                        <h4 className="font-medium text-slate-800 text-sm">{course.name}</h4>
                        <p className="text-xs text-slate-600">{course.department} • {course.credits}학점</p>
                        <p className="text-xs text-green-600">{course.reason}</p>
                      </div>
                      <div className="text-right">
                        <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                          {course.difficulty}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-2 text-slate-500">
                    <p className="text-xs">C학점 과목이 없어 추천할 과목이 없습니다</p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
              <h4 className="font-medium text-slate-800 mb-1">학습 전략</h4>
              <ul className="text-sm text-slate-700 space-y-1">
                <li>• C학점 과목 우선 재수강 권장</li>
                <li>• 유사 과목으로 기초 실력 보완</li>
                <li>• 현재 평균: {calculateGPA()}/4.5</li>
                <li>• 목표 학점 4.0 달성까지 {calculateRetakeRecommendations().length > 0 ? '1-2학기' : '추가 과목 필요'} 소요</li>
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