import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  User,
  Mail,
  Phone,
  Edit,
  Save,
  X,
  RefreshCcw,
  BarChart3,
  TrendingUp,
  BookOpen,
  Layers,
  Database,
  Sparkles,
  Target,
} from 'lucide-react';
import softwareCourses from '../data/softwareCourses.json';
import GoogleSignInButton from '../components/GoogleSignInButton';
import { useAuth } from '../context/AuthContext';

const GPA_PROFILE_KEY = 'courseai:gpa:profile';
const GPA_COURSES_KEY = 'courseai:gpa:courses';
const GPA_REQUIREMENTS_KEY = 'courseai:gpa:requirements';

const DEFAULT_GPA_PROFILE = {
  currentGpa: '0',
  targetGpa: '4.0',
  totalCredits: '0',
  requiredCredits: '130',
};

const DEFAULT_GPA_REQUIREMENTS = [
  { id: 'majorCore', label: '전공 필수', completed: '0', required: '30' },
  { id: 'majorElective', label: '전공 선택', completed: '0', required: '42' },
  { id: 'liberalArts', label: '교양', completed: '0', required: '36' },
];

const GRADE_TO_POINT = {
  'A+': 4.5,
  A0: 4.0,
  'B+': 3.5,
  B0: 3.0,
  'C+': 2.5,
  C0: 2.0,
  'D+': 1.5,
  D0: 1.0,
  F: 0.0,
};

const toNumber = (value, fallback = 0) => {
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
};

const loadFromStorage = (key, fallback) => {
  if (typeof window === 'undefined') return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    return parsed;
  } catch (error) {
    console.warn(`Failed to parse storage key: ${key}`, error);
    return fallback;
  }
};

const sanitizeCourses = (courses) => {
  if (!Array.isArray(courses)) return [];
  return courses.map((course) => ({
    name: course.name || '',
    credits: toNumber(course.credits, 0),
    grade: course.grade && GRADE_TO_POINT[course.grade] !== undefined ? course.grade : 'A+',
  }));
};

const sanitizeRequirements = (requirements) => {
  if (!Array.isArray(requirements) || !requirements.length) {
    return DEFAULT_GPA_REQUIREMENTS;
  }

  return requirements.map((req, index) => ({
    id: req.id || `requirement-${index}`,
    label: req.label || '',
    completed: typeof req.completed === 'number' ? String(req.completed) : req.completed || '0',
    required: typeof req.required === 'number' ? String(req.required) : req.required || '0',
  }));
};

const MyPage = () => {
  const { user, loading: authLoading, isAuthenticating, authError, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editableProfile, setEditableProfile] = useState(null);
  const [interestInput, setInterestInput] = useState('');
  const [profileError, setProfileError] = useState(null);
  const [gpaProfile, setGpaProfile] = useState(() => ({
    ...DEFAULT_GPA_PROFILE,
    ...loadFromStorage(GPA_PROFILE_KEY, {}),
  }));
  const [gpaCourses, setGpaCourses] = useState(() =>
    sanitizeCourses(loadFromStorage(GPA_COURSES_KEY, []))
  );
  const [gpaRequirements, setGpaRequirements] = useState(() =>
    sanitizeRequirements(loadFromStorage(GPA_REQUIREMENTS_KEY, DEFAULT_GPA_REQUIREMENTS))
  );
  const [lastRefreshed, setLastRefreshed] = useState(new Date());
  const [aiEndpoint, setAiEndpoint] = useState('');

  useEffect(() => {
    const base = (process.env.REACT_APP_AI_API_BASE_URL || '').replace(/\/$/, '');
    if (base) {
      setAiEndpoint(base);
    } else if (typeof window !== 'undefined') {
      setAiEndpoint(`${window.location.protocol}//${window.location.hostname}:5003`);
    }
  }, []);

  useEffect(() => {
    if (!user) {
      setEditableProfile(null);
      setInterestInput('');
      return;
    }
    setEditableProfile({
      name: user.name || '',
      major: user.major || '',
      semester: user.semester ?? '',
      email: user.email || '',
      phone: user.phone || '',
      goal: user.goal || '',
      bio: user.bio || '',
    });
    setInterestInput((user.interests || []).join(', '));
    setProfileError(null);
  }, [user]);

  const refreshAcademicData = useCallback(() => {
    setGpaProfile({
      ...DEFAULT_GPA_PROFILE,
      ...loadFromStorage(GPA_PROFILE_KEY, {}),
    });
    setGpaCourses(sanitizeCourses(loadFromStorage(GPA_COURSES_KEY, [])));
    setGpaRequirements(
      sanitizeRequirements(loadFromStorage(GPA_REQUIREMENTS_KEY, DEFAULT_GPA_REQUIREMENTS))
    );
    setLastRefreshed(new Date());
  }, []);

  useEffect(() => {
    refreshAcademicData();
  }, [refreshAcademicData]);

  const courseStats = useMemo(() => {
    if (!Array.isArray(softwareCourses) || !softwareCourses.length) {
      return {
        totalCourses: 0,
        totalProfessors: 0,
        averageCredits: 0,
        averageHours: 0,
        courseTypeEntries: [],
        targetGradeEntries: [],
        semesterEntries: [],
        lectureMethodEntries: [],
        classTypeEntries: [],
        topProfessors: [],
        topTags: [],
        highCreditCourses: [],
      };
    }

    let totalCredits = 0;
    let totalHours = 0;
    const professorCounts = new Map();
    const courseTypeCounts = new Map();
    const targetGradeCounts = new Map();
    const semesterCounts = new Map();
    const lectureMethodCounts = new Map();
    const classTypeCounts = new Map();
    const tagCounts = new Map();

    softwareCourses.forEach((course) => {
      const credits = toNumber(course.credits, 0);
      const hours = toNumber(course.hours, 0);
      totalCredits += credits;
      totalHours += hours;

      const professor = course.professor || '미확인 교수';
      professorCounts.set(professor, (professorCounts.get(professor) || 0) + 1);

      const courseType = course.course_type || '분류 없음';
      courseTypeCounts.set(courseType, (courseTypeCounts.get(courseType) || 0) + 1);

      const targetGrade = course.target_grade || '학년 정보 없음';
      targetGradeCounts.set(targetGrade, (targetGradeCounts.get(targetGrade) || 0) + 1);

      const semester = course.semester || '학기 정보 없음';
      semesterCounts.set(semester, (semesterCounts.get(semester) || 0) + 1);

      const lectureMethod = course.lecture_method || course.details?.lecture_method || '미정';
      lectureMethodCounts.set(
        lectureMethod,
        (lectureMethodCounts.get(lectureMethod) || 0) + 1
      );

      const classType = course.class_type || '형태 미정';
      classTypeCounts.set(classType, (classTypeCounts.get(classType) || 0) + 1);

      if (Array.isArray(course.tags)) {
        course.tags.forEach((tag) => {
          if (!tag) return;
          tagCounts.set(tag, (tagCounts.get(tag) || 0) + 1);
        });
      }
    });

    const sortedEntries = (map) =>
      Array.from(map.entries()).sort((a, b) => b[1] - a[1]);

    return {
      totalCourses: softwareCourses.length,
      totalProfessors: professorCounts.size,
      averageCredits: softwareCourses.length ? totalCredits / softwareCourses.length : 0,
      averageHours: softwareCourses.length ? totalHours / softwareCourses.length : 0,
      courseTypeEntries: sortedEntries(courseTypeCounts),
      targetGradeEntries: sortedEntries(targetGradeCounts),
      semesterEntries: sortedEntries(semesterCounts),
      lectureMethodEntries: sortedEntries(lectureMethodCounts),
      classTypeEntries: sortedEntries(classTypeCounts),
      topProfessors: sortedEntries(professorCounts).slice(0, 5),
      topTags: sortedEntries(tagCounts).slice(0, 8),
      highCreditCourses: softwareCourses
        .filter((course) => toNumber(course.credits, 0) >= 4)
        .sort((a, b) => toNumber(b.credits, 0) - toNumber(a.credits, 0))
        .slice(0, 5)
        .map((course) => ({
          course_name: course.course_name,
          credits: toNumber(course.credits, 0),
          professor: course.professor,
          course_type: course.course_type,
          semester: course.semester,
        })),
    };
  }, []);

  const plannedCredits = useMemo(
    () => gpaCourses.reduce((sum, course) => sum + toNumber(course.credits, 0), 0),
    [gpaCourses]
  );

  const plannedPoints = useMemo(
    () =>
      gpaCourses.reduce(
        (sum, course) =>
          sum + toNumber(course.credits, 0) * (GRADE_TO_POINT[course.grade] || 0),
        0
      ),
    [gpaCourses]
  );

  const plannedAverageGpa = plannedCredits > 0 ? plannedPoints / plannedCredits : 0;

  const retakeCandidates = useMemo(() => {
    if (!plannedCredits) return [];
    return gpaCourses
      .filter((course) => (GRADE_TO_POINT[course.grade] || 0) < (GRADE_TO_POINT['A0'] || 4.0))
      .map((course) => {
        const currentPoint = GRADE_TO_POINT[course.grade] || 0;
        const potentialPoint = 4.5;
        const impactValue =
          plannedCredits > 0
            ? ((potentialPoint - currentPoint) * toNumber(course.credits, 0)) / plannedCredits
            : 0;
        if (impactValue <= 0) return null;
        return {
          name: course.name || '미입력 과목',
          currentGrade: course.grade,
          credits: toNumber(course.credits, 0),
          impact: impactValue.toFixed(2),
        };
      })
      .filter(Boolean)
      .sort((a, b) => parseFloat(b.impact) - parseFloat(a.impact))
      .slice(0, 3);
  }, [gpaCourses, plannedCredits]);

  const currentGpa = toNumber(gpaProfile.currentGpa, 0);
  const targetGpa = toNumber(gpaProfile.targetGpa, 0);
  const totalCredits = toNumber(gpaProfile.totalCredits, 0);
  const requiredCredits = toNumber(gpaProfile.requiredCredits, 0);
  const remainingCredits = Math.max(requiredCredits - totalCredits, 0);
  const gpaGap = Math.max(targetGpa - plannedAverageGpa, 0);

  const formattedRefreshed = useMemo(
    () =>
      new Intl.DateTimeFormat('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      }).format(lastRefreshed),
    [lastRefreshed]
  );

  const handleSaveProfile = async () => {
    if (!editableProfile) return;

    const sanitizedInterests = interestInput
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);

    const semesterValue = editableProfile.semester;
    let semesterNumber = null;
    if (semesterValue !== '' && semesterValue !== null && semesterValue !== undefined) {
      const numeric = Number(semesterValue);
      if (Number.isFinite(numeric)) {
        semesterNumber = numeric;
      } else {
        setProfileError('학기는 숫자로 입력해주세요.');
        return;
      }
    }

    try {
      setProfileError(null);
      await updateProfile({
        name: editableProfile.name,
        major: editableProfile.major,
        goal: editableProfile.goal,
        bio: editableProfile.bio,
        phone: editableProfile.phone,
        semester: semesterNumber,
        interests: sanitizedInterests,
      });
      setIsEditing(false);
    } catch (error) {
      setProfileError(error.message);
    }
  };

  const handleCancelEdit = () => {
    if (!user) return;
    setEditableProfile({
      name: user.name || '',
      major: user.major || '',
      semester: user.semester ?? '',
      email: user.email || '',
      phone: user.phone || '',
      goal: user.goal || '',
      bio: user.bio || '',
    });
    setInterestInput((user.interests || []).join(', '));
    setIsEditing(false);
    setProfileError(null);
  };

  const systemHighlights = useMemo(
    () => [
      {
        icon: Layers,
        title: '강의 데이터 파이프라인',
        description:
          'scripts/export_software_courses.py 스크립트가 2025-2.xlsx에서 강의를 추출해 softwareCourses.json으로 변환합니다.',
      },
      {
        icon: Database,
        title: '백엔드 API',
        description:
          'backend/api/lecture_api.py의 /api/software-courses 엔드포인트가 엑셀 기반 강의 데이터를 제공합니다.',
      },
      {
        icon: Sparkles,
        title: 'AI 상담 엔드포인트',
        description: `${aiEndpoint}/api/rag/chat 를 통해 RAG 기반 강의 상담을 제공합니다.`,
      },
    ],
    [aiEndpoint]
  );

  const renderDistribution = (entries, total) =>
    entries.slice(0, 5).map(([label, count]) => {
      const percent = total > 0 ? Math.round((count / total) * 100) : 0;
      return (
        <div key={label} className="space-y-1">
          <div className="flex justify-between text-xs text-slate-600">
            <span>{label}</span>
            <span>
              {count}개 • {percent}%
            </span>
          </div>
          <div className="w-full h-2 bg-slate-200 rounded-full">
            <div
              className="h-2 bg-sky-500 rounded-full transition-all"
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>
      );
    });

  if (authLoading || isAuthenticating) {
    return (
      <div className="h-[calc(100vh-200px)] flex items-center justify-center text-slate-500 text-sm">
        Google 로그인 상태를 확인하고 있습니다...
      </div>
    );
  }

  if (!user) {
    return (
      <div className="h-[calc(100vh-200px)] flex flex-col items-center justify-center gap-4 text-slate-600 text-sm">
        <p className="text-center">
          마이페이지 기능을 사용하려면 Google 계정으로 로그인해주세요.
        </p>
        <GoogleSignInButton />
        {authError && (
          <p className="text-xs text-rose-500 max-w-xs text-center">{authError}</p>
        )}
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-200px)] flex flex-col">
      <div className="bg-white border-b border-slate-200 p-4 rounded-t-xl">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-sky-100 rounded-lg">
              <User className="w-6 h-6 text-sky-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-800">마이페이지</h2>
              <p className="text-sm text-slate-500">
                소프트웨어학과 강의 데이터와 학습 계획을 한눈에 확인하세요.
              </p>
            </div>
          </div>
          <button
            onClick={refreshAcademicData}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-sm border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <RefreshCcw className="w-4 h-4" />
            데이터 새로고침
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 bg-slate-50 space-y-4">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
          <div className="bg-white border border-slate-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500">소프트웨어학과 강의 수</p>
                <p className="text-2xl font-semibold text-slate-800">
                  {courseStats.totalCourses.toLocaleString()}개
                </p>
              </div>
              <BarChart3 className="w-6 h-6 text-sky-500" />
            </div>
            <p className="mt-2 text-xs text-slate-500">
              평균 {courseStats.averageCredits.toFixed(2)}학점 • 수업시간{' '}
              {courseStats.averageHours.toFixed(1)}시간
            </p>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500">지도 교수 수</p>
                <p className="text-2xl font-semibold text-slate-800">
                  {courseStats.totalProfessors.toLocaleString()}명
                </p>
              </div>
              <BookOpen className="w-6 h-6 text-emerald-500" />
            </div>
            <p className="mt-2 text-xs text-slate-500">
              상위 교수: {courseStats.topProfessors.map(([name]) => name).slice(0, 2).join(', ') || '데이터 없음'}
            </p>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500">현재 입력된 평점</p>
                <p className="text-2xl font-semibold text-slate-800">
                  {currentGpa.toFixed(2)}
                </p>
              </div>
              <TrendingUp className="w-6 h-6 text-indigo-500" />
            </div>
            <p className="mt-2 text-xs text-slate-500">
              목표 {targetGpa.toFixed(2)} • 격차 {gpaGap.toFixed(2)}
            </p>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500">졸업까지 남은 학점</p>
                <p className="text-2xl font-semibold text-slate-800">
                  {remainingCredits.toLocaleString()}학점
                </p>
              </div>
              <Target className="w-6 h-6 text-rose-500" />
            </div>
            <p className="mt-2 text-xs text-slate-500">
              누적 {totalCredits.toLocaleString()}학점 / 필요 {requiredCredits.toLocaleString()}학점
            </p>
          </div>
        </div>

        {/* Profile Section */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-slate-800">개인 정보</h3>
              <p className="text-xs text-slate-500">내 학습 목표와 관심사를 정리하세요.</p>
            </div>
            {isEditing ? (
              <div className="flex items-center gap-2">
                <button
                  onClick={handleSaveProfile}
                  className="inline-flex items-center gap-2 px-3 py-1.5 text-sm bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
                >
                  <Save className="w-4 h-4" />
                  저장
                </button>
                <button
                  onClick={handleCancelEdit}
                  className="inline-flex items-center gap-2 px-3 py-1.5 text-sm border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  <X className="w-4 h-4" />
                  취소
                </button>
              </div>
            ) : (
              <button
            onClick={() => {
              setProfileError(null);
              setIsEditing(true);
            }}
                className="inline-flex items-center gap-2 px-3 py-1.5 text-sm border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 transition-colors"
              >
                <Edit className="w-4 h-4" />
                편집
              </button>
            )}
          </div>

      {profileError && (
        <p className="text-xs text-rose-500">{profileError}</p>
      )}

          {isEditing ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs text-slate-500">이름</label>
                <input
                  type="text"
                  value={editableProfile?.name || ''}
                  onChange={(e) =>
                    setEditableProfile((prev) => ({ ...prev, name: e.target.value }))
                  }
                  className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-400"
                  placeholder="이름을 입력하세요"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-500">학과</label>
                <input
                  type="text"
                  value={editableProfile?.major || ''}
                  onChange={(e) =>
                    setEditableProfile((prev) => ({ ...prev, major: e.target.value }))
                  }
                  className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-400"
                  placeholder="전공을 입력하세요"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-500">학기</label>
                <input
                  type="number"
                  min="1"
                  value={editableProfile?.semester ?? ''}
                  onChange={(e) =>
                    setEditableProfile((prev) => ({
                      ...prev,
                      semester: e.target.value,
                    }))
                  }
                  className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-400"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-500">이메일</label>
                <input
                  type="email"
                  value={editableProfile?.email || ''}
                  readOnly
                  disabled
                  className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-400"
                  placeholder="example@univ.ac.kr"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-500">연락처</label>
                <input
                  type="tel"
                  value={editableProfile?.phone || ''}
                  onChange={(e) =>
                    setEditableProfile((prev) => ({ ...prev, phone: e.target.value }))
                  }
                  className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-400"
                  placeholder="010-1234-5678"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-500">학습 목표</label>
                <input
                  type="text"
                  value={editableProfile?.goal || ''}
                  onChange={(e) =>
                    setEditableProfile((prev) => ({ ...prev, goal: e.target.value }))
                  }
                  className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-400"
                  placeholder="예: AI 전문가"
                />
              </div>
              <div className="md:col-span-2 space-y-1">
                <label className="text-xs text-slate-500">자기소개</label>
                <textarea
                  value={editableProfile?.bio || ''}
                  onChange={(e) =>
                    setEditableProfile((prev) => ({ ...prev, bio: e.target.value }))
                  }
                  rows={3}
                  className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-400"
                  placeholder="학습 계획이나 관심사를 자유롭게 적어주세요."
                />
              </div>
              <div className="md:col-span-2 space-y-1">
                <label className="text-xs text-slate-500">관심 분야 (쉼표로 구분)</label>
                <input
                  type="text"
                  value={interestInput}
                  onChange={(e) => setInterestInput(e.target.value)}
                  className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-400"
                  placeholder="프론트엔드, 데이터분석, AI"
                />
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-700">
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-sky-600" />
                <span>{user?.name || '이름 없음'}</span>
              </div>
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-emerald-600" />
                <span>{user?.major || '전공 미입력'} • {user?.semester ? `${user.semester}학기` : '학기 정보 없음'}</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-indigo-600" />
                <span>{user?.email || '이메일 미등록'}</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-rose-500" />
                <span>{user?.phone || '연락처 미등록'}</span>
              </div>
              <div className="md:col-span-2 space-y-1">
                <p className="text-xs text-slate-500 uppercase">Goal</p>
                <p>{user?.goal || '학습 목표를 설정해보세요.'}</p>
              </div>
              <div className="md:col-span-2 space-y-1">
                <p className="text-xs text-slate-500 uppercase">Bio</p>
                <p>{user?.bio || '자기소개를 추가해보세요.'}</p>
              </div>
              <div className="md:col-span-2 space-y-1">
                <p className="text-xs text-slate-500 uppercase">Interests</p>
                <div className="flex flex-wrap gap-2">
                  {(user?.interests || []).length ? (
                    user.interests.map((interest) => (
                      <span
                        key={interest}
                        className="px-2 py-1 text-xs bg-sky-100 text-sky-700 rounded-full border border-sky-200"
                      >
                        {interest}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500">관심 분야가 등록되지 않았습니다.</span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Academic Planner */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-slate-800">학업 플래너 & GPA</h3>
              <p className="text-xs text-slate-500">
                학점 계산기 데이터를 연동해 재수강과 학점 전략을 확인하세요. 최근 갱신: {formattedRefreshed}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border border-slate-200 rounded-lg p-3 bg-slate-50">
              <p className="text-xs text-slate-500">계획된 과목 수</p>
              <p className="text-xl font-semibold text-slate-800">{gpaCourses.length}개</p>
              <p className="text-xs text-slate-500 mt-1">총 {plannedCredits}학점</p>
            </div>
            <div className="border border-slate-200 rounded-lg p-3 bg-slate-50">
              <p className="text-xs text-slate-500">예상 평균 평점</p>
              <p className="text-xl font-semibold text-sky-600">{plannedAverageGpa.toFixed(2)}</p>
              <p className="text-xs text-slate-500 mt-1">이번 학기 계획 기준</p>
            </div>
            <div className="border border-slate-200 rounded-lg p-3 bg-slate-50">
              <p className="text-xs text-slate-500">재수강 추천</p>
              <p className="text-xl font-semibold text-emerald-600">
                {retakeCandidates.length ? `${retakeCandidates.length}과목` : '추천 없음'}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {retakeCandidates.length
                  ? `예상 상승 +${retakeCandidates[0].impact}p`
                  : '재수강 필요 과목이 없습니다.'}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-slate-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-slate-800 mb-2">재수강 우선순위</h4>
              <div className="space-y-2">
                {retakeCandidates.length ? (
                  retakeCandidates.map((course) => (
                    <div
                      key={course.name}
                      className="flex items-center justify-between border border-slate-200 rounded-lg px-3 py-2 text-sm"
                    >
                      <div>
                        <p className="font-medium text-slate-800">{course.name}</p>
                        <p className="text-xs text-slate-500">
                          현재 {course.currentGrade} • {course.credits}학점
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-emerald-600 font-semibold">
                          +{course.impact}p
                        </p>
                        <p className="text-2xs text-slate-400 uppercase">평점 개선</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500 text-center border border-slate-200 rounded-lg py-3">
                    학점 계산기에서 낮은 성적 과목을 입력하면 자동으로 추천됩니다.
                  </p>
                )}
              </div>
            </div>

            <div className="border border-slate-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-slate-800 mb-2">졸업 요건 진행률</h4>
              <div className="space-y-3">
                {gpaRequirements.map((req) => {
                  const completed = toNumber(req.completed, 0);
                  const required = Math.max(toNumber(req.required, 0), 0);
                  const percent = required > 0 ? Math.min((completed / required) * 100, 100) : 0;
                  return (
                    <div key={req.id} className="space-y-1">
                      <div className="flex justify-between text-xs text-slate-600">
                        <span>{req.label || '카테고리 미정'}</span>
                        <span>
                          {completed}/{required}
                        </span>
                      </div>
                      <div className="w-full h-2 bg-slate-200 rounded-full">
                        <div
                          className="h-2 bg-indigo-500 rounded-full transition-all"
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Course Insights */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-slate-800">강의 데이터 인사이트</h3>
              <p className="text-xs text-slate-500">
                softwareCourses.json 기반으로 소프트웨어학과 강의 현황을 분석했습니다.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="border border-slate-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-slate-800 mb-2">이수구분 분포</h4>
              <div className="space-y-2 text-xs text-slate-600">
                {courseStats.courseTypeEntries.length ? (
                  renderDistribution(courseStats.courseTypeEntries, courseStats.totalCourses)
                ) : (
                  <p className="text-xs text-slate-500">강의 분포 데이터를 불러오는 중입니다.</p>
                )}
              </div>
            </div>

            <div className="border border-slate-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-slate-800 mb-2">학년 대상</h4>
              <div className="space-y-2 text-xs text-slate-600">
                {courseStats.targetGradeEntries.length ? (
                  renderDistribution(courseStats.targetGradeEntries, courseStats.totalCourses)
                ) : (
                  <p className="text-xs text-slate-500">학년 분포 데이터를 불러오는 중입니다.</p>
                )}
              </div>
            </div>

            <div className="border border-slate-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-slate-800 mb-2">최근 학기 개설</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                {courseStats.semesterEntries.slice(0, 4).map(([semester, count]) => (
                  <li key={semester} className="flex justify-between">
                    <span>{semester}</span>
                    <span className="text-xs text-slate-500">{count}과목</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-slate-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-slate-800 mb-2">상위 담당 교수</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                {courseStats.topProfessors.length ? (
                  courseStats.topProfessors.map(([name, count]) => (
                    <li key={name} className="flex justify-between items-center">
                      <span>{name}</span>
                      <span className="text-xs text-slate-500">{count}과목</span>
                    </li>
                  ))
                ) : (
                  <li className="text-xs text-slate-500">교수 정보를 불러오는 중입니다.</li>
                )}
              </ul>
            </div>
            <div className="border border-slate-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-slate-800 mb-2">자주 등장한 태그</h4>
              <div className="flex flex-wrap gap-2">
                {courseStats.topTags.length ? (
                  courseStats.topTags.map(([tag, count]) => (
                    <span
                      key={tag}
                      className="px-2 py-1 text-xs bg-emerald-100 text-emerald-700 rounded-full border border-emerald-200"
                    >
                      {tag} • {count}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500">태그 데이터가 없습니다.</span>
                )}
              </div>
            </div>
          </div>

          <div className="border border-slate-200 rounded-lg p-3">
            <h4 className="text-sm font-semibold text-slate-800 mb-2">고학점 강의 Top 5</h4>
            <div className="space-y-2 text-sm text-slate-600">
              {courseStats.highCreditCourses.length ? (
                courseStats.highCreditCourses.map((course) => (
                  <div
                    key={course.course_name}
                    className="flex items-center justify-between border border-slate-200 rounded-lg px-3 py-2"
                  >
                    <div>
                      <p className="font-medium text-slate-800">{course.course_name}</p>
                      <p className="text-xs text-slate-500">
                        {course.semester} • {course.course_type || '분류 없음'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-sky-600">{course.credits}학점</p>
                      <p className="text-xs text-slate-500">{course.professor || '교수 미정'}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 text-center">
                  고학점 강의 데이터를 불러오는 중입니다.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* System Highlights */}
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <h3 className="text-base font-semibold text-slate-800 mb-3">시스템 구성 요약</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {systemHighlights.map(({ icon: Icon, title, description }) => (
              <div key={title} className="border border-slate-200 rounded-lg p-3 space-y-2">
                <Icon className="w-5 h-5 text-sky-600" />
                <h4 className="text-sm font-semibold text-slate-800">{title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyPage;

