import React, { useState } from 'react';
import { 
  User, Mail, Phone, MapPin, Calendar, 
  BookOpen, Star, Edit, Save, X, Camera,
  BarChart3, Target, Clock, Heart, Calculator,
  MessageSquare
} from 'lucide-react';

const ProfilePage = ({ mockUserProfile }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedProfile, setEditedProfile] = useState(mockUserProfile);

  const handleSave = () => {
    setIsEditing(false);
    console.log('프로필 업데이트:', editedProfile);
  };

  const handleCancel = () => {
    setEditedProfile(mockUserProfile);
    setIsEditing(false);
  };

  return (
    <div className="h-[calc(100vh-200px)] flex flex-col">
      {/* Profile Header */}
      <div className="bg-white border-b border-slate-200 p-4 rounded-t-xl">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-sky-500 rounded-full flex items-center justify-center">
            <User className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-slate-800">{mockUserProfile.name}</h2>
            <p className="text-sm text-slate-500">{mockUserProfile.major} • {mockUserProfile.semester}학기</p>
          </div>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="flex items-center gap-2 px-3 py-1.5 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors text-sm"
          >
            <Edit className="w-4 h-4" />
            편집
          </button>
        </div>
      </div>

      {/* Profile Stats */}
      <div className="bg-white border-b border-slate-200 p-4">
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center p-3 bg-sky-50 rounded-lg border border-sky-100">
            <div className="text-xl font-bold text-sky-600">{mockUserProfile.gpa}</div>
            <div className="text-xs text-slate-600">평점평균</div>
          </div>
          <div className="text-center p-3 bg-emerald-50 rounded-lg border border-emerald-100">
            <div className="text-xl font-bold text-emerald-600">{mockUserProfile.totalCredits}</div>
            <div className="text-xs text-slate-600">이수학점</div>
          </div>
          <div className="text-center p-3 bg-orange-50 rounded-lg border border-orange-100">
            <div className="text-xl font-bold text-orange-600">{mockUserProfile.requiredCredits - mockUserProfile.totalCredits}</div>
            <div className="text-xs text-slate-600">남은학점</div>
          </div>
          <div className="text-center p-3 bg-purple-50 rounded-lg border border-purple-100">
            <div className="text-xl font-bold text-purple-600">{Math.round((mockUserProfile.totalCredits / mockUserProfile.requiredCredits) * 100)}%</div>
            <div className="text-xs text-slate-600">진행률</div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 bg-slate-50 space-y-4">
        <div className="grid grid-cols-3 gap-4">
          {/* Recent Activity */}
          <div className="col-span-2 bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">최근 활동</h3>
            <div className="space-y-2">
              {[
                { content: '웹프로그래밍 강의평을 작성했습니다', time: '2시간 전', icon: Star, color: 'amber' },
                { content: '데이터베이스 강의를 북마크했습니다', time: '1일 전', icon: Heart, color: 'red' },
                { content: '노팀플 강의를 검색했습니다', time: '2일 전', icon: BookOpen, color: 'sky' },
                { content: '학점 계산기를 사용했습니다', time: '3일 전', icon: Calculator, color: 'emerald' }
              ].map((activity, index) => {
                const Icon = activity.icon;
                return (
                  <div key={index} className="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-lg transition-colors">
                    <div className={`w-6 h-6 bg-${activity.color}-100 rounded-full flex items-center justify-center`}>
                      <Icon className={`w-3 h-3 text-${activity.color}-600`} />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-slate-800">{activity.content}</p>
                      <p className="text-xs text-slate-500">{activity.time}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">빠른 작업</h3>
            <div className="space-y-2">
              <button className="w-full flex items-center gap-2 p-2 text-left hover:bg-sky-50 rounded-lg transition-colors border border-transparent hover:border-sky-200">
                <div className="p-1.5 bg-sky-100 rounded-lg">
                  <BarChart3 className="w-4 h-4 text-sky-600" />
                </div>
                <span className="text-slate-700 text-sm">학점 분석</span>
              </button>
              <button className="w-full flex items-center gap-2 p-2 text-left hover:bg-emerald-50 rounded-lg transition-colors border border-transparent hover:border-emerald-200">
                <div className="p-1.5 bg-emerald-100 rounded-lg">
                  <Target className="w-4 h-4 text-emerald-600" />
                </div>
                <span className="text-slate-700 text-sm">졸업 요건</span>
              </button>
              <button className="w-full flex items-center gap-2 p-2 text-left hover:bg-orange-50 rounded-lg transition-colors border border-transparent hover:border-orange-200">
                <div className="p-1.5 bg-orange-100 rounded-lg">
                  <Clock className="w-4 h-4 text-orange-600" />
                </div>
                <span className="text-slate-700 text-sm">시간표</span>
              </button>
              <button className="w-full flex items-center gap-2 p-2 text-left hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-200">
                <div className="p-1.5 bg-red-100 rounded-lg">
                  <Heart className="w-4 h-4 text-red-600" />
                </div>
                <span className="text-slate-700 text-sm">북마크</span>
              </button>
            </div>
          </div>
        </div>

        {/* My Reviews */}
        <div className="bg-white rounded-lg border border-slate-200 p-4">
          <h3 className="font-semibold text-slate-800 mb-3">내가 작성한 강의평</h3>
          <div className="space-y-2">
            {[
              { course: '웹프로그래밍', professor: '박교수', rating: 5, date: '2024.06.15', content: '정말 좋은 강의였습니다. 실무 중심의 내용이 도움이 되었어요.' },
              { course: '데이터베이스', professor: '이교수', rating: 4, date: '2024.06.10', content: '과제는 많지만 실력 향상에 도움됩니다. 추천해요!' }
            ].map((review, index) => (
              <div key={index} className="border border-slate-200 rounded-lg p-3 hover:border-sky-200 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h4 className="font-medium text-slate-800">{review.course}</h4>
                    <p className="text-sm text-slate-600">{review.professor}</p>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className={`w-3 h-3 ${i < review.rating ? 'text-amber-400 fill-current' : 'text-slate-300'}`} />
                      ))}
                    </div>
                    <p className="text-xs text-slate-500">{review.date}</p>
                  </div>
                </div>
                <p className="text-sm text-slate-700">{review.content}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Preferences & Settings */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">관심 분야</h3>
            <div className="flex flex-wrap gap-2">
              {mockUserProfile.preferences.map((pref, index) => (
                <span key={index} className="bg-sky-100 text-sky-800 px-2 py-1 rounded-full text-sm border border-sky-200">
                  {pref}
                </span>
              ))}
            </div>
            <button className="mt-2 text-sm text-sky-600 hover:text-sky-700 transition-colors">+ 추가</button>
          </div>

          <div className="bg-white rounded-lg border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-800 mb-3">설정</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 hover:bg-slate-50 rounded-lg transition-colors">
                <span className="text-sm text-slate-700">이메일 알림</span>
                <input type="checkbox" className="rounded border-slate-300 text-sky-600 focus:ring-sky-500" defaultChecked />
              </div>
              <div className="flex items-center justify-between p-2 hover:bg-slate-50 rounded-lg transition-colors">
                <span className="text-sm text-slate-700">푸시 알림</span>
                <input type="checkbox" className="rounded border-slate-300 text-sky-600 focus:ring-sky-500" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;