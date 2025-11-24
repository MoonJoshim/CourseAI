import React, { useState, useMemo, useEffect } from 'react';
import { Minus, Plus, Calculator, RotateCcw } from 'lucide-react';

const PROFILE_STORAGE_KEY = 'courseai:gpa:profile';
const COURSES_STORAGE_KEY = 'courseai:gpa:courses';

const gradeToPoint = {
  'A+': 4.5, 'A0': 4.0, 'B+': 3.5, 'B0': 3.0,
  'C+': 2.5, 'C0': 2.0, 'D+': 1.5, 'D0': 1.0, F: 0.0,
};

const gradeOptions = Object.keys(gradeToPoint);

const createDefaultProfile = () => ({
  currentGpa: '0',
  targetGpa: '4.0',
  totalCredits: '0',
  requiredCredits: '140',
});

const createDefaultCourses = () => [{ name: '', credits: 3, grade: 'A+' }];

const toNumber = (value) => {
  const num = parseFloat(value);
  return Number.isFinite(num) ? num : 0;
};

const formatDecimal = (value, digits = 2) => {
  const num = Number(value);
  return Number.isFinite(num) ? num.toFixed(digits) : (0).toFixed(digits);
};

const loadProfile = () => {
  const defaultProfile = createDefaultProfile();
  if (typeof window === 'undefined') return defaultProfile;
  try {
    const stored = window.localStorage.getItem(PROFILE_STORAGE_KEY);
    if (!stored) return defaultProfile;
    const parsed = JSON.parse(stored);
    return { ...defaultProfile, ...parsed };
  } catch (error) {
    return defaultProfile;
  }
};

const loadCourses = () => {
  const defaultCourses = createDefaultCourses();
  if (typeof window === 'undefined') return defaultCourses;
  try {
    const stored = window.localStorage.getItem(COURSES_STORAGE_KEY);
    if (!stored) return defaultCourses;
    const parsed = JSON.parse(stored);
    if (!Array.isArray(parsed) || parsed.length === 0) return defaultCourses;
    return parsed.map((course) => ({
      name: course.name || '',
      credits: Number.isFinite(Number(course.credits)) ? Number(course.credits) : 3,
      grade: gradeOptions.includes(course.grade) ? course.grade : 'A+',
    }));
  } catch (error) {
    return defaultCourses;
  }
};

const GPAPage = () => {
  const [profile, setProfile] = useState(loadProfile);
  const [selectedCourses, setSelectedCourses] = useState(loadCourses);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
  }, [profile]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(COURSES_STORAGE_KEY, JSON.stringify(selectedCourses));
  }, [selectedCourses]);

  const totalCourseCredits = useMemo(
    () => selectedCourses.reduce((sum, course) => sum + (Number(course.credits) || 0), 0),
    [selectedCourses]
  );

  const totalCoursePoints = useMemo(
    () =>
      selectedCourses.reduce(
        (sum, course) =>
          sum + (Number(course.credits) || 0) * (gradeToPoint[course.grade] || 0),
        0
      ),
    [selectedCourses]
  );

  const plannedGpa = totalCourseCredits > 0 ? totalCoursePoints / totalCourseCredits : 0;
  const plannedGpaDisplay = formatDecimal(plannedGpa);

  const currentGpaNum = toNumber(profile.currentGpa);
  const targetGpaNum = toNumber(profile.targetGpa || '4.0');
  const totalCreditsNum = toNumber(profile.totalCredits);
  const requiredCreditsNum = toNumber(profile.requiredCredits);
  const remainingCredits = Math.max(requiredCreditsNum - totalCreditsNum, 0);
  const gpaGap = Math.max(targetGpaNum - plannedGpa, 0);

  const handleProfileChange = (field) => (event) => {
    const { value } = event.target;
    setProfile((prev) => ({ ...prev, [field]: value }));
  };

  const addCourse = () => {
    setSelectedCourses((prev) => [...prev, { name: '', credits: 3, grade: 'A+' }]);
  };

  const removeCourse = (index) => {
    setSelectedCourses((prev) => {
      if (prev.length <= 1) return prev;
      return prev.filter((_, i) => i !== index);
    });
  };

  const updateCourse = (index, field, value) => {
    setSelectedCourses((prev) =>
      prev.map((course, i) => {
        if (i !== index) return course;
        if (field === 'credits') {
          return { ...course, credits: Number(value) };
        }
        return { ...course, [field]: value };
      })
    );
  };

  const resetData = () => {
    const defaultProfile = createDefaultProfile();
    const defaultCourses = createDefaultCourses();
    setProfile(defaultProfile);
    setSelectedCourses(defaultCourses);
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem(PROFILE_STORAGE_KEY);
      window.localStorage.removeItem(COURSES_STORAGE_KEY);
    }
  };

  // C+ 이하 과목 재수강 추천
  const retakeRecommendations = useMemo(() => {
    const lowGradeCourses = selectedCourses.filter(course => 
      ['C+', 'C0', 'D+', 'D0', 'F'].includes(course.grade) && course.name.trim()
    );

    if (lowGradeCourses.length === 0) return [];

    const recommendations = lowGradeCourses.map(course => {
      const currentPoint = gradeToPoint[course.grade];
      const credits = Number(course.credits);
      const potentialGain = (4.5 - currentPoint) * credits / totalCourseCredits;

      return {
        courseName: course.name,
        currentGrade: course.grade,
        credits: credits,
        currentPoint: currentPoint.toFixed(1),
        potentialGain: potentialGain.toFixed(2),
        priority: potentialGain,
        recommendation: currentPoint <= 2.0 
          ? '필수 재수강 권장 - 학점 영향도가 큽니다'
          : '재수강 고려 - 평점 향상에 도움이 됩니다'
      };
    });

    return recommendations.sort((a, b) => b.priority - a.priority);
  }, [selectedCourses, totalCourseCredits]);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 mb-1">학점 계산</h1>
              <p className="text-sm text-slate-600">학기별 수강 계획을 입력하고 목표 학점을 관리하세요</p>
            </div>
            <button
              onClick={resetData}
              className="inline-flex items-center gap-2 px-3 py-2 text-sm border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              초기화
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-3">
            <div className="bg-slate-50 px-4 py-3 rounded-lg border border-slate-200">
              <div className="text-xs text-slate-600 mb-1">현재 평점</div>
              <input
                type="number"
                min="0"
                max="4.5"
                step="0.01"
                value={profile.currentGpa}
                onChange={handleProfileChange('currentGpa')}
                className="w-full text-lg font-bold text-slate-900 bg-transparent border-0 focus:outline-none p-0"
              />
            </div>

            <div className="bg-slate-50 px-4 py-3 rounded-lg border border-slate-200">
              <div className="text-xs text-slate-600 mb-1">목표 평점</div>
              <input
                type="number"
                min="0"
                max="4.5"
                step="0.01"
                value={profile.targetGpa}
                onChange={handleProfileChange('targetGpa')}
                className="w-full text-lg font-bold text-slate-900 bg-transparent border-0 focus:outline-none p-0"
              />
            </div>

            <div className="bg-slate-50 px-4 py-3 rounded-lg border border-slate-200">
              <div className="text-xs text-slate-600 mb-1">이수 학점</div>
              <input
                type="number"
                min="0"
                step="1"
                value={profile.totalCredits}
                onChange={handleProfileChange('totalCredits')}
                className="w-full text-lg font-bold text-slate-900 bg-transparent border-0 focus:outline-none p-0"
              />
            </div>

            <div className="bg-slate-50 px-4 py-3 rounded-lg border border-slate-200">
              <div className="text-xs text-slate-600 mb-1">졸업 필요</div>
              <div className="text-lg font-bold text-slate-900">{requiredCreditsNum}학점</div>
              <div className="text-xs text-slate-500">남은 {remainingCredits}학점</div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-5">
        {/* Retake Recommendations */}
        {retakeRecommendations.length > 0 && (
          <div className="bg-white border-2 border-red-500 rounded-lg p-5 mb-4">
            <h3 className="text-base font-bold text-red-600 mb-3">⚠️ 재수강 추천</h3>
            <p className="text-sm text-slate-700 mb-4">C+ 이하 성적의 과목이 발견되었습니다. 재수강을 고려해보세요.</p>
            <div className="space-y-2">
              {retakeRecommendations.map((rec, index) => (
                <div key={index} className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-bold text-slate-900 mb-1">{rec.courseName}</h4>
                      <p className="text-sm text-slate-600">
                        현재 성적: <span className="font-semibold text-red-600">{rec.currentGrade}</span> ({rec.currentPoint}점) • {rec.credits}학점
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-slate-900">+{rec.potentialGain}</p>
                      <p className="text-xs text-slate-500">예상 향상</p>
                    </div>
                  </div>
                  <p className="text-xs text-red-700 bg-red-50 px-3 py-2 rounded border border-red-200">
                    {rec.recommendation}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* GPA Calculator */}
          <div className="bg-white rounded-lg border border-slate-200 p-5">
            <h3 className="text-base font-bold text-slate-900 mb-4">학점 계산기</h3>

            <div className="space-y-2 mb-4">
              {selectedCourses.map((course, index) => (
                <div
                  key={index}
                  className="flex gap-2 items-center p-2 rounded-lg border border-slate-200 bg-slate-50"
                >
                  <input
                    type="text"
                    value={course.name}
                    onChange={(e) => updateCourse(index, 'name', e.target.value)}
                    className="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none bg-white"
                    placeholder="강의명 입력"
                  />
                  <select
                    value={course.credits}
                    onChange={(e) => updateCourse(index, 'credits', e.target.value)}
                    className="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none"
                  >
                    <option value={1}>1학점</option>
                    <option value={2}>2학점</option>
                    <option value={3}>3학점</option>
                    <option value={4}>4학점</option>
                  </select>
                  <select
                    value={course.grade}
                    onChange={(e) => updateCourse(index, 'grade', e.target.value)}
                    className="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none"
                  >
                    {gradeOptions.map((grade) => (
                      <option key={grade} value={grade}>{grade}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => removeCourse(index)}
                    className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:text-slate-300"
                    disabled={selectedCourses.length <= 1}
                  >
                    <Minus className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>

            <button
              onClick={addCourse}
              className="w-full py-2.5 border-2 border-dashed border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600 mb-4 text-sm font-medium transition-all"
            >
              <Plus className="w-4 h-4 inline mr-1" />
              강의 추가
            </button>

            <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-700">예상 평균 학점</span>
                <span className="text-2xl font-bold text-slate-900">{plannedGpaDisplay}</span>
              </div>
              <div className="text-sm text-slate-600 space-y-1">
                <div>총 {totalCourseCredits}학점</div>
                <div className="text-xs text-slate-500">
                  가중합 {totalCoursePoints.toFixed(1)}점 / {totalCourseCredits}학점
                </div>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-white rounded-lg border border-slate-200 p-5">
            <h3 className="text-base font-bold text-slate-900 mb-4">학점 현황</h3>

            <div className="space-y-3">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <div className="text-xs text-slate-600 mb-1">현재 평점</div>
                <div className="text-2xl font-bold text-slate-900">{formatDecimal(currentGpaNum)}</div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <div className="text-xs text-slate-600 mb-1">이번 학기 예상</div>
                <div className="text-2xl font-bold text-slate-900">{plannedGpaDisplay}</div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <div className="text-xs text-slate-600 mb-1">목표 평점</div>
                <div className="text-2xl font-bold text-slate-900">{formatDecimal(targetGpaNum)}</div>
                <div className="text-xs text-slate-500 mt-1">차이 {formatDecimal(gpaGap)}점</div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <div className="flex justify-between items-center mb-2">
                  <div className="text-xs text-slate-600">졸업 진행률</div>
                  <div className="text-sm font-semibold text-slate-900">
                    {((totalCreditsNum / requiredCreditsNum) * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 mb-2">
                  <div
                    className="h-2 rounded-full transition-all"
                    style={{
                      width: `${Math.min((totalCreditsNum / requiredCreditsNum) * 100, 100)}%`,
                      backgroundColor: '#8FCACA'
                    }}
                  ></div>
                </div>
                <div className="text-xs text-slate-600">
                  {totalCreditsNum} / {requiredCreditsNum}학점 (남은 {remainingCredits}학점)
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GPAPage;
