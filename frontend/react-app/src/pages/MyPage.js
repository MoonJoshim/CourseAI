import React, { useState } from 'react';
import { User, Edit, Save, X } from 'lucide-react';
import AuthForm from '../components/AuthForm';
import { useAuth } from '../context/AuthContext';

const MyPage = () => {
  const { user, loading: authLoading, isAuthenticating, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editableProfile, setEditableProfile] = useState(null);
  const [profileError, setProfileError] = useState(null);

  const handleEditClick = () => {
    setEditableProfile({
      name: user?.name || '',
      major: user?.major || '',
      semester: user?.semester || '',
    });
    setIsEditing(true);
    setProfileError(null);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditableProfile(null);
    setProfileError(null);
  };

  const handleSaveProfile = async () => {
    if (!editableProfile) return;

    try {
      setProfileError(null);
      await updateProfile(editableProfile);
      setIsEditing(false);
      setEditableProfile(null);
    } catch (error) {
      setProfileError(error.message || '프로필 업데이트에 실패했습니다.');
    }
  };

  const handleProfileChange = (field, value) => {
    setEditableProfile((prev) => ({ ...prev, [field]: value }));
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-50">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="bg-white rounded-lg border p-8" style={{borderColor: '#B6CFB6'}}>
            <h2 className="text-2xl font-bold text-slate-900 mb-6 text-center">로그인</h2>
            <AuthForm />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b" style={{borderColor: '#B6CFB6'}}>
        <div className="max-w-4xl mx-auto px-6 py-5">
          <h1 className="text-2xl font-bold text-slate-900 mb-1">마이페이지</h1>
          <p className="text-sm text-slate-600">내 정보를 확인하고 수정하세요</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-6">
        {/* Profile Card */}
        <div className="bg-white rounded-lg border p-6 mb-6" style={{borderColor: '#B6CFB6'}}>
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-4">
              {user.picture ? (
                <img
                  src={user.picture}
                  alt={user.name || 'Profile'}
                  className="w-20 h-20 rounded-full object-cover border-2"
                  style={{borderColor: '#8FCACA'}}
                  referrerPolicy="no-referrer"
                />
              ) : (
                <div className="w-20 h-20 rounded-full flex items-center justify-center text-white text-2xl font-bold" style={{backgroundColor: '#8FCACA'}}>
                  <User className="w-10 h-10" />
                </div>
              )}
              <div>
                <h2 className="text-xl font-bold text-slate-900">{user.name || '사용자'}</h2>
                <p className="text-sm text-slate-600">{user.email}</p>
              </div>
            </div>

            {!isEditing ? (
              <button
                onClick={handleEditClick}
                className="flex items-center gap-2 px-4 py-2 border rounded-lg text-sm font-medium text-slate-700 hover:text-slate-900 transition-all"
                style={{borderColor: '#B6CFB6'}}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#D4F0F0'}
                onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
              >
                <Edit className="w-4 h-4" />
                편집
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={handleSaveProfile}
                  className="flex items-center gap-2 px-4 py-2 text-white rounded-lg text-sm font-medium transition-all"
                  style={{backgroundColor: '#8FCACA'}}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#7AB8B8'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#8FCACA'}
                >
                  <Save className="w-4 h-4" />
                  저장
                </button>
                <button
                  onClick={handleCancelEdit}
                  className="flex items-center gap-2 px-4 py-2 border rounded-lg text-sm font-medium text-slate-700 transition-all"
                  style={{borderColor: '#B6CFB6'}}
                >
                  <X className="w-4 h-4" />
                  취소
                </button>
              </div>
            )}
          </div>

          {profileError && (
            <div className="mb-4 p-3 rounded-lg border" style={{backgroundColor: '#FFE6E6', borderColor: '#FF9999'}}>
              <p className="text-sm text-red-700">{profileError}</p>
            </div>
          )}

          {/* Profile Info */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">이름</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editableProfile?.name || ''}
                  onChange={(e) => handleProfileChange('name', e.target.value)}
                  className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 text-sm"
                  style={{borderColor: '#B6CFB6'}}
                  placeholder="이름을 입력하세요"
                />
              ) : (
                <p className="text-base text-slate-900">{user.name || '미설정'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">이메일</label>
              <p className="text-base text-slate-900">{user.email}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">전공</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editableProfile?.major || ''}
                  onChange={(e) => handleProfileChange('major', e.target.value)}
                  className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 text-sm"
                  style={{borderColor: '#B6CFB6'}}
                  placeholder="전공을 입력하세요"
                />
              ) : (
                <p className="text-base text-slate-900">{user.major || '미설정'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">학년/학기</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editableProfile?.semester || ''}
                  onChange={(e) => handleProfileChange('semester', e.target.value)}
                  className="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 text-sm"
                  style={{borderColor: '#B6CFB6'}}
                  placeholder="예: 3학년 1학기"
                />
              ) : (
                <p className="text-base text-slate-900">{user.semester || '미설정'}</p>
              )}
            </div>
          </div>
        </div>

        {/* Account Info */}
        <div className="bg-white rounded-lg border p-6" style={{borderColor: '#B6CFB6'}}>
          <h3 className="text-lg font-bold text-slate-900 mb-4">계정 정보</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b" style={{borderColor: '#CCE2CB'}}>
              <span className="text-sm text-slate-600">로그인 방식</span>
              <span className="text-sm font-medium text-slate-900">Google</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b" style={{borderColor: '#CCE2CB'}}>
              <span className="text-sm text-slate-600">계정 상태</span>
              <span className="text-sm font-medium px-3 py-1 rounded-full" style={{backgroundColor: '#D4F0F0', color: '#2C5F5F'}}>
                활성
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-slate-600">가입일</span>
              <span className="text-sm font-medium text-slate-900">
                {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : '-'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyPage;
