import React, { useState, useMemo, useEffect } from 'react';
import { Minus, Plus, Target, Calculator, RotateCcw, Trash2 } from 'lucide-react';

const PROFILE_STORAGE_KEY = 'courseai:gpa:profile';
const COURSES_STORAGE_KEY = 'courseai:gpa:courses';
const REQUIREMENTS_STORAGE_KEY = 'courseai:gpa:requirements';

const gradeToPoint = {
  'A+': 4.5,
  'A0': 4.0,
  'B+': 3.5,
  'B0': 3.0,
  'C+': 2.5,
  'C0': 2.0,
  'D+': 1.5,
  'D0': 1.0,
  F: 0.0,
};

const gradeOptions = Object.keys(gradeToPoint);

const createDefaultProfile = () => ({
  currentGpa: '0',
  targetGpa: '4.0',
  totalCredits: '0',
  requiredCredits: '130',
});

const createDefaultCourses = () => [
  { name: '', credits: 3, grade: 'A+' },
];

const createDefaultRequirements = () => [
  { id: 'majorCore', label: '전공 필수', completed: '0', required: '30' },
  { id: 'majorElective', label: '전공 선택', completed: '0', required: '42' },
  { id: 'liberalArts', label: '교양', completed: '0', required: '36' },
];

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
  if (typeof window === 'undefined') {
    return defaultProfile;
  }

  try {
    const stored = window.localStorage.getItem(PROFILE_STORAGE_KEY);
    if (!stored) {
      return defaultProfile;
    }
    const parsed = JSON.parse(stored);
    return { ...defaultProfile, ...parsed };
  } catch (error) {
    console.warn('Failed to parse stored GPA profile', error);
    return defaultProfile;
  }
};

const loadCourses = () => {
  const defaultCourses = createDefaultCourses();
  if (typeof window === 'undefined') {
    return defaultCourses;
  }

  try {
    const stored = window.localStorage.getItem(COURSES_STORAGE_KEY);
    if (!stored) {
      return defaultCourses;
    }
    const parsed = JSON.parse(stored);
    if (!Array.isArray(parsed) || parsed.length === 0) {
      return defaultCourses;
    }
    return parsed.map((course) => ({
      name: course.name || '',
      credits: Number.isFinite(Number(course.credits)) ? Number(course.credits) : 3,
      grade: gradeOptions.includes(course.grade) ? course.grade : 'A+',
    }));
  } catch (error) {
    console.warn('Failed to parse stored GPA courses', error);
    return defaultCourses;
  }
};

const loadRequirements = () => {
  const defaults = createDefaultRequirements();
  if (typeof window === 'undefined') {
    return defaults;
  }

  try {
    const stored = window.localStorage.getItem(REQUIREMENTS_STORAGE_KEY);
    if (!stored) {
      return defaults;
    }
    const parsed = JSON.parse(stored);
    if (!Array.isArray(parsed) || parsed.length === 0) {
      return defaults;
    }
    return parsed.map((req, index) => ({
      id: req.id || `requirement-${index}`,
      label: req.label || '',
      completed: typeof req.completed === 'number' ? String(req.completed) : (req.completed || '0'),
      required: typeof req.required === 'number' ? String(req.required) : (req.required || '0'),
    }));
  } catch (error) {
    console.warn('Failed to parse stored GPA requirements', error);
    return defaults;
  }
};

const GPAPage = () => {
  const [profile, setProfile] = useState(loadProfile);
  const [selectedCourses, setSelectedCourses] = useState(loadCourses);
  const [requirements, setRequirements] = useState(loadRequirements);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
  }, [profile]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(COURSES_STORAGE_KEY, JSON.stringify(selectedCourses));
  }, [selectedCourses]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(REQUIREMENTS_STORAGE_KEY, JSON.stringify(requirements));
  }, [requirements]);

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

  const retakeRecommendations = useMemo(() => {
    if (!totalCourseCredits) {
      return [];
    }

    return selectedCourses
      .filter((course) => gradeToPoint[course.grade] < targetGpaNum)
      .map((course) => {
        const currentPoint = gradeToPoint[course.grade] || 0;
        const potentialPoint = 4.5;
        const credits = Number(course.credits) || 0;
        const impactValue =
          totalCourseCredits > 0
            ? ((potentialPoint - currentPoint) * credits) / totalCourseCredits
            : 0;

        if (impactValue <= 0) {
          return null;
        }

        return {
          name: course.name || '미입력',
          currentGrade: course.grade,
          credits,
          impact: `+${impactValue.toFixed(2)}`,
          impactValue,
        };
      })
      .filter(Boolean)
      .sort((a, b) => b.impactValue - a.impactValue)
      .slice(0, 3);
  }, [selectedCourses, targetGpaNum, totalCourseCredits]);

  const similarCourseRecommendations = useMemo(() => {
    const cGradeCourses = selectedCourses.filter((course) =>
      ['C+', 'C0', 'D+', 'D0', 'F'].includes(course.grade)
    );

    const similarCourses = [];

    cGradeCourses.forEach((course) => {
      const courseName = (course.name || '').toLowerCase();
      const credits = Number(course.credits) || 0;

      if (courseName.includes('프로그래밍') || courseName.includes('programming')) {
        similarCourses.push(
          {
            name: '고급프로그래밍',
            department: '컴퓨터공학과',
            credits,
            reason: '프로그래밍 기초 강화',
            difficulty: '중급',
          },
          {
            name: '소프트웨어공학',
            department: '컴퓨터공학과',
            credits,
            reason: '설계 및 프로젝트 경험 강화',
            difficulty: '중급',
          }
        );
      }

      if (courseName.includes('데이터') || courseName.includes('data')) {
        similarCourses.push(
          {
            name: '데이터마이닝',
            department: '컴퓨터공학과',
            credits,
            reason: '데이터 분석 심화',
            difficulty: '고급',
          },
          {
            name: '빅데이터처리',
            department: '컴퓨터공학과',
            credits,
            reason: '대용량 데이터 처리 훈련',
            difficulty: '고급',
          }
        );
      }

      if (courseName.includes('수학') || courseName.includes('math')) {
        similarCourses.push(
          {
            name: '이산수학',
            department: '수학과',
            credits,
            reason: '컴퓨터과학 기초 수학',
            difficulty: '중급',
          },
          {
            name: '확률통계',
            department: '수학과',
            credits,
            reason: '통계적 사고력 향상',
            difficulty: '중급',
          }
        );
      }

      if (courseName.includes('네트워크') || courseName.includes('network')) {
        similarCourses.push(
          {
            name: '네트워크보안',
            department: '컴퓨터공학과',
            credits,
            reason: '네트워크 보안 심화',
            difficulty: '고급',
          },
          {
            name: '클라우드컴퓨팅',
            department: '컴퓨터공학과',
            credits,
            reason: '분산 시스템 이해',
            difficulty: '고급',
          }
        );
      }
    });

    const uniqueCourses = similarCourses.filter(
      (course, index, self) => index === self.findIndex((c) => c.name === course.name)
    );

    return uniqueCourses.slice(0, 3);
  }, [selectedCourses]);

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

  const handleRequirementChange = (id, field, value) => {
    setRequirements((prev) =>
      prev.map((req) => (req.id === id ? { ...req, [field]: value } : req))
    );
  };

  const addRequirement = () => {
    const newRequirement = {
      id: `requirement-${Date.now()}`,
      label: '',
      completed: '0',
      required: '0',
    };
    setRequirements((prev) => [...prev, newRequirement]);
  };

  const removeRequirement = (id) => {
    setRequirements((prev) => (prev.length <= 1 ? prev : prev.filter((req) => req.id !== id)));
  };

  const resetData = () => {
    const defaultProfile = createDefaultProfile();
    const defaultCourses = createDefaultCourses();
    const defaultRequirements = createDefaultRequirements();

    setProfile(defaultProfile);
    setSelectedCourses(defaultCourses);
    setRequirements(defaultRequirements);

    if (typeof window !== 'undefined') {
      window.localStorage.removeItem(PROFILE_STORAGE_KEY);
      window.localStorage.removeItem(COURSES_STORAGE_KEY);
      window.localStorage.removeItem(REQUIREMENTS_STORAGE_KEY);
    }
  };

  const maxPossibleGpa =
    totalCourseCredits > 0
      ? selectedCourses.reduce(
          (sum, course) => sum + (Number(course.credits) || 0) * 4.5,
          0
        ) / totalCourseCredits
      : 0;

  return (
    <div className="h-[calc(100vh-200px)] flex flex-col">
      {/* GPA Header */}
      <div className="bg-white border-b border-slate-200 p-4 rounded-t-xl">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-sky-100 rounded-lg">
              <Calculator className="w-6 h-6 text-sky-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-800">학점 계산</h2>
              <p className="text-sm text-slate-500">
                학기별 수강 계획을 입력하고 목표 학점을 직접 관리해보세요.
              </p>
            </div>
          </div>
          <button
            onClick={resetData}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-sm border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            초기화
          </button>
        </div>
      </div>

      {/* Current Status */}
      <div className="bg-white border-b border-slate-200 p-4">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div className="p-3 bg-sky-50 rounded-lg border border-sky-100">
            <label className="text-xs text-slate-600 mb-1 block">현재 평점</label>
            <input
              type="number"
              min="0"
              max="4.5"
              step="0.01"
              value={profile.currentGpa}
              onChange={handleProfileChange('currentGpa')}
              className="w-full text-xl font-bold text-sky-600 bg-transparent border border-sky-200 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-sky-400"
            />
            <p className="mt-1 text-xs text-slate-500">현재까지 누적 평점을 직접 입력하세요.</p>
          </div>

          <div className="p-3 bg-sky-50 rounded-lg border border-sky-100">
            <label className="text-xs text-slate-600 mb-1 block">목표 평점</label>
            <input
              type="number"
              min="0"
              max="4.5"
              step="0.01"
              value={profile.targetGpa}
              onChange={handleProfileChange('targetGpa')}
              className="w-full text-xl font-bold text-sky-600 bg-transparent border border-sky-200 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-sky-400"
            />
            <p className="mt-1 text-xs text-slate-500">
              예상 평균 {plannedGpaDisplay}/4.5 • 차이 {formatDecimal(gpaGap)}
            </p>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <label className="text-xs text-slate-600 mb-1 block">이수 학점</label>
            <input
              type="number"
              min="0"
              step="1"
              value={profile.totalCredits}
              onChange={handleProfileChange('totalCredits')}
              className="w-full text-xl font-bold text-slate-700 bg-transparent border border-slate-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-sky-400"
            />
            <p className="mt-1 text-xs text-slate-500">
              입력한 이수 학점은 졸업 요건 계산에 반영됩니다.
            </p>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <label className="text-xs text-slate-600 mb-1 block">졸업 필요 학점</label>
            <input
              type="number"
              min="0"
              step="1"
              value={profile.requiredCredits}
              onChange={handleProfileChange('requiredCredits')}
              className="w-full text-xl font-bold text-slate-700 bg-transparent border border-slate-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-sky-400"
            />
            <p className="mt-1 text-xs text-slate-500">
              남은 학점 {remainingCredits}학점
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 bg-slate-50 space-y-4">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {/* GPA Calculator */}
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">학점 계산기</h3>

            <div className="space-y-2 mb-4">
              {selectedCourses.map((course, index) => (
                <div
                  key={`${course.name}-${index}`}
                  className="flex flex-col gap-2 rounded-lg border border-slate-200 p-2 md:flex-row md:items-center"
                >
                  <input
                    type="text"
                    value={course.name}
                    onChange={(e) => updateCourse(index, 'name', e.target.value)}
                    className="flex-1 px-2 py-1 text-sm border border-transparent rounded focus:outline-none focus:border-sky-300 bg-slate-50 md:bg-transparent"
                    placeholder="강의명"
                  />
                  <div className="flex items-center gap-2">
                    <select
                      value={course.credits}
                      onChange={(e) => updateCourse(index, 'credits', e.target.value)}
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
                      {gradeOptions.map((grade) => (
                        <option key={grade} value={grade}>
                          {grade}
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={() => removeCourse(index)}
                      className="p-1 text-red-500 hover:bg-red-50 rounded transition-colors disabled:text-slate-300 disabled:hover:bg-transparent"
                      disabled={selectedCourses.length <= 1}
                    >
                      <Minus className="w-3 h-3" />
                    </button>
                  </div>
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
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <span className="font-medium text-slate-800">예상 평균 학점</span>
                <span className="text-lg font-bold text-sky-600">{plannedGpaDisplay}/4.5</span>
              </div>
              <div className="text-sm text-slate-600 space-y-1 mt-2">
                <div>총 {totalCourseCredits}학점</div>
                <div className="text-xs text-slate-500">
                  가중합 {totalCoursePoints.toFixed(1)}점 / {totalCourseCredits}학점
                </div>
              </div>
            </div>
          </div>

          {/* Retake Recommendations */}
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">재수강 & 대체 과목 추천</h3>

            <div className="mb-4">
              <h4 className="text-sm font-medium text-slate-700 mb-2">재수강 시 효과</h4>
              <div className="space-y-2">
                {retakeRecommendations.length > 0 ? (
                  retakeRecommendations.map((course, index) => (
                    <div
                      key={`${course.name}-${index}`}
                      className="flex items-center justify-between p-2 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
                    >
                      <div>
                        <h4 className="font-medium text-slate-800 text-sm">{course.name}</h4>
                        <p className="text-xs text-slate-600">
                          현재 {course.currentGrade} • {course.credits}학점
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-sky-600 text-sm">{course.impact}</p>
                        <p className="text-xs text-slate-500">평균 상승</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-3 text-slate-500 border border-slate-200 rounded-lg">
                    <p className="text-xs">
                      목표보다 낮은 성적의 과목이 없거나 입력된 과목이 부족합니다.
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-sm font-medium text-slate-700 mb-2">대체 과목 탐색</h4>
              <div className="space-y-2">
                {similarCourseRecommendations.length > 0 ? (
                  similarCourseRecommendations.map((course, index) => (
                    <div
                      key={`${course.name}-${index}`}
                      className="flex items-center justify-between p-2 border border-green-200 rounded-lg hover:bg-green-50 transition-colors"
                    >
                      <div>
                        <h4 className="font-medium text-slate-800 text-sm">{course.name}</h4>
                        <p className="text-xs text-slate-600">
                          {course.department} • {course.credits}학점
                        </p>
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
                  <div className="text-center py-3 text-slate-500 border border-slate-200 rounded-lg">
                    <p className="text-xs">C 이하 성적의 과목을 입력하면 대체 과목을 제안해요.</p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
              <h4 className="font-medium text-slate-800 mb-1">학습 전략 메모</h4>
              <ul className="text-sm text-slate-700 space-y-1">
                <li>• 예상 평균 {plannedGpaDisplay} / 목표 {formatDecimal(targetGpaNum)}</li>
                <li>
                  • 목표까지 필요 상승분 {formatDecimal(gpaGap)}{' '}
                  {gpaGap > 0 ? '(재수강으로 메우기)' : '(목표 달성)'}
                </li>
                <li>• 계획된 학점 {totalCourseCredits}학점</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Graduation Requirements */}
        <div className="bg-white rounded-lg border border-slate-200 p-4 space-y-4">
          <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <h3 className="font-semibold text-slate-800">졸업 요건 관리</h3>
            <div className="flex gap-2">
              <button
                onClick={addRequirement}
                className="px-3 py-1.5 text-sm border border-sky-200 text-sky-700 rounded-lg hover:bg-sky-50 transition-colors"
              >
                카테고리 추가
              </button>
            </div>
          </div>

          <div className="space-y-3">
            {requirements.map((req) => {
              const completed = toNumber(req.completed);
              const required = Math.max(toNumber(req.required), 0);
              const percent = required > 0 ? Math.min((completed / required) * 100, 100) : 0;
              const remaining = Math.max(required - completed, 0);

              return (
                <div
                  key={req.id}
                  className="border border-slate-200 rounded-lg p-3 bg-slate-50 space-y-2"
                >
                  <div className="grid gap-2 md:grid-cols-[2fr_repeat(2,1fr)_auto] md:items-center">
                    <input
                      type="text"
                      value={req.label}
                      onChange={(e) => handleRequirementChange(req.id, 'label', e.target.value)}
                      placeholder="카테고리 이름 (예: 전공 필수)"
                      className="px-2 py-1 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-sky-400 bg-white"
                    />
                    <input
                      type="number"
                      min="0"
                      step="1"
                      value={req.completed}
                      onChange={(e) =>
                        handleRequirementChange(req.id, 'completed', e.target.value)
                      }
                      className="px-2 py-1 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-sky-400 bg-white"
                      placeholder="이수 학점"
                    />
                    <input
                      type="number"
                      min="0"
                      step="1"
                      value={req.required}
                      onChange={(e) =>
                        handleRequirementChange(req.id, 'required', e.target.value)
                      }
                      className="px-2 py-1 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-sky-400 bg-white"
                      placeholder="필요 학점"
                    />
                    <button
                      onClick={() => removeRequirement(req.id)}
                      className="px-2 py-1 text-xs border border-red-200 text-red-500 rounded hover:bg-red-50 transition-colors disabled:text-slate-300 disabled:border-slate-200 disabled:hover:bg-transparent"
                      disabled={requirements.length <= 1}
                    >
                      <Trash2 className="w-3 h-3 inline mr-1" />
                      삭제
                    </button>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-xs text-slate-600">
                      <span>
                        진행률 {formatDecimal(percent, 1)}% • 남은 학점 {remaining}학점
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-sky-600 h-2 rounded-full transition-all"
                        style={{ width: `${percent}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* GPA Prediction */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <h3 className="font-semibold text-slate-800 mb-3">학점 변화 시뮬레이션</h3>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="p-3 border border-slate-200 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500 mb-1">현재 입력 평점</p>
              <p className="text-2xl font-semibold text-slate-800">{formatDecimal(currentGpaNum)}</p>
              <p className="text-xs text-slate-500 mt-1">누적 학점 기준</p>
            </div>
            <div className="p-3 border border-slate-200 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500 mb-1">이번 학기 예상 평균</p>
              <p className="text-2xl font-semibold text-sky-600">{plannedGpaDisplay}</p>
              <p className="text-xs text-slate-500 mt-1">입력한 강의 기준</p>
            </div>
            <div className="p-3 border border-slate-200 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500 mb-1">이론상 최대 평균</p>
              <p className="text-2xl font-semibold text-emerald-600">
                {formatDecimal(maxPossibleGpa)}
              </p>
              <p className="text-xs text-slate-500 mt-1">모든 과목 A+ 가정</p>
            </div>
          </div>

          <div className="mt-4 bg-slate-50 border border-slate-200 rounded-lg p-3 flex items-start gap-3">
            <div className="p-2 bg-sky-100 rounded-full">
              <Target className="w-5 h-5 text-sky-600" />
            </div>
            <div className="text-sm text-slate-700 space-y-1">
              <p>
                현재 평점 {formatDecimal(currentGpaNum)}에서 입력된 계획을 그대로 이수하면{' '}
                {plannedGpaDisplay}을(를) 기대할 수 있습니다.
              </p>
              <p>
                목표 평점 {formatDecimal(targetGpaNum)}까지는 {formatDecimal(gpaGap)}p가
                필요하며, 재수강 추천을 반영하면 더 빠르게 도달할 수 있어요.
              </p>
              <p>졸업까지 남은 학점은 약 {remainingCredits}학점입니다.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GPAPage;