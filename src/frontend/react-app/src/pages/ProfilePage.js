import React, { useState } from 'react';
import { 
  User, Mail, Phone, MapPin, Calendar, GraduationCap, 
  Award, BookOpen, Star, Edit, Save, X, Camera,
  BarChart3, Target, Clock, Heart, Calculator
} from 'lucide-react';

const ProfilePage = ({ mockUserProfile }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedProfile, setEditedProfile] = useState(mockUserProfile);

  const handleSave = () => {
    // 실제로는 API 호출로 프로필 업데이트
    setIsEditing(false);
    console.log('프로필 업데이트:', editedProfile);
  };

  const handleCancel = () => {
    setEditedProfile(mockUserProfile);
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-8 border border-blue-100">
        <div className="flex items-start gap-6">
          {/* Profile Picture */}
          <div className="relative">
            <div className="w-24 h-24 bg-blue-500 rounded-full flex items-center justify-center">
              <User className="w-12 h-12 text-white" />
            </div>
            <button className="absolute -bottom-2 -right-2 w-8 h-8 bg-white rounded-full shadow-md flex items-center justify-center hover:bg-gray-50">
              <Camera className="w-4 h-4 text-gray-600" />
            </button>
          </div>

          {/* Profile Info */}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-4">
              <div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedProfile.name}
                    onChange={(e) => setEditedProfile({...editedProfile, name: e.target.value})}
                    className="text-2xl font-bold bg-white px-3 py-1 rounded border"
                  />
                ) : (
                  <h1 className="text-2xl font-bold text-gray-900">{mockUserProfile.name}</h1>
                )}
                <p className="text-gray-600">{mockUserProfile.major} • {mockUserProfile.semester}학기</p>
              </div>
              
              <div className="flex gap-2">
                {isEditing ? (
                  <>
                    <button
                      onClick={handleSave}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <Save className="w-4 h-4" />
                      저장
                    </button>
                    <button
                      onClick={handleCancel}
                      className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      <X className="w-4 h-4" />
                      취소
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    <Edit className="w-4 h-4" />
                    편집
                  </button>
                )}
              </div>
            </div>

            {/* Contact Info */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-gray-500" />
                <span>student@university.ac.kr</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-gray-500" />
                <span>010-1234-5678</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-gray-500" />
                <span>서울특별시</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-500" />
                <span>2018년 입학</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="col-span-2 space-y-6">
          {/* Academic Stats */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">학업 현황</h3>
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{mockUserProfile.gpa}</div>
                <div className="text-sm text-gray-600">평점평균</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{mockUserProfile.totalCredits}</div>
                <div className="text-sm text-gray-600">이수학점</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{mockUserProfile.requiredCredits - mockUserProfile.totalCredits}</div>
                <div className="text-sm text-gray-600">남은학점</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{Math.round((mockUserProfile.totalCredits / mockUserProfile.requiredCredits) * 100)}%</div>
                <div className="text-sm text-gray-600">진행률</div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">최근 활동</h3>
            <div className="space-y-4">
              {[
                { type: 'review', content: '웹프로그래밍 강의평을 작성했습니다', time: '2시간 전', icon: Star },
                { type: 'bookmark', content: '데이터베이스 강의를 북마크했습니다', time: '1일 전', icon: Heart },
                { type: 'search', content: '노팀플 강의를 검색했습니다', time: '2일 전', icon: BookOpen },
                { type: 'gpa', content: '학점 계산기를 사용했습니다', time: '3일 전', icon: Calculator }
              ].map((activity, index) => {
                const Icon = activity.icon;
                return (
                  <div key={index} className="flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <Icon className="w-4 h-4 text-gray-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">{activity.content}</p>
                      <p className="text-xs text-gray-500">{activity.time}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* My Reviews */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">내가 작성한 강의평</h3>
            <div className="space-y-4">
              {[
                { course: '웹프로그래밍', professor: '박교수', rating: 5, date: '2024.06.15', content: '정말 좋은 강의였습니다. 실무 중심의 내용이 도움이 되었어요.' },
                { course: '데이터베이스', professor: '이교수', rating: 4, date: '2024.06.10', content: '과제는 많지만 실력 향상에 도움됩니다. 추천해요!' },
                { course: '소프트웨어공학', professor: '김교수', rating: 5, date: '2024.06.05', content: '팀플 없고 성적도 잘 주셔서 만족합니다.' }
              ].map((review, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h4 className="font-semibold">{review.course}</h4>
                      <p className="text-sm text-gray-600">{review.professor}</p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} className={`w-4 h-4 ${i < review.rating ? 'text-yellow-500 fill-current' : 'text-gray-300'}`} />
                        ))}
                      </div>
                      <p className="text-xs text-gray-500">{review.date}</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">{review.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">빠른 작업</h3>
            <div className="space-y-3">
              <button className="w-full flex items-center gap-3 p-3 text-left hover:bg-gray-50 rounded-lg">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                <span>학점 분석 보기</span>
              </button>
              <button className="w-full flex items-center gap-3 p-3 text-left hover:bg-gray-50 rounded-lg">
                <Target className="w-5 h-5 text-green-600" />
                <span>졸업 요건 확인</span>
              </button>
              <button className="w-full flex items-center gap-3 p-3 text-left hover:bg-gray-50 rounded-lg">
                <Clock className="w-5 h-5 text-orange-600" />
                <span>시간표 관리</span>
              </button>
              <button className="w-full flex items-center gap-3 p-3 text-left hover:bg-gray-50 rounded-lg">
                <Heart className="w-5 h-5 text-red-600" />
                <span>북마크 강의</span>
              </button>
            </div>
          </div>

          {/* Preferences */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">관심 분야</h3>
            <div className="flex flex-wrap gap-2">
              {mockUserProfile.preferences.map((pref, index) => (
                <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                  {pref}
                </span>
              ))}
            </div>
            <button className="mt-3 text-sm text-blue-600 hover:text-blue-700">+ 관심 분야 추가</button>
          </div>

          {/* Achievements */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">달성 뱃지</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { name: '리뷰어', icon: '📝', desc: '강의평 10개 작성' },
                { name: '탐험가', icon: '🔍', desc: '50개 강의 검색' },
                { name: '계획자', icon: '📅', desc: '시간표 완성' },
                { name: '성실한', icon: '⭐', desc: '매일 접속 7일' }
              ].map((badge, index) => (
                <div key={index} className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-1">{badge.icon}</div>
                  <div className="text-xs font-semibold">{badge.name}</div>
                  <div className="text-xs text-gray-500">{badge.desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Settings */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold mb-4">설정</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">이메일 알림</span>
                <input type="checkbox" className="rounded" defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">푸시 알림</span>
                <input type="checkbox" className="rounded" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">다크 모드</span>
                <input type="checkbox" className="rounded" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
