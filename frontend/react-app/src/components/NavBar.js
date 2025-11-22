import React, { useMemo } from 'react';
import { 
  Search, Calculator, Brain, Bell, User, MessageSquare, List, LogOut
} from 'lucide-react';
import GoogleSignInButton from './GoogleSignInButton';
import { useAuth } from '../context/AuthContext';

const NavBar = ({ currentPage, setCurrentPage }) => {
  const { user, loading, isAuthenticating, signOut } = useAuth();

  const displayName = useMemo(() => {
    if (user?.name) return user.name;
    if (user?.email) return user.email.split('@')[0];
    return '로그인이 필요합니다';
  }, [user]);

  const displaySecondary = useMemo(() => {
    if (!user) return 'Google 계정으로 로그인하세요';
    return user.major || user.email || '프로필 정보 없음';
  }, [user]);

  const userInitial = useMemo(() => {
    if (user?.name) return user.name.trim().charAt(0).toUpperCase();
    if (user?.email) return user.email.trim().charAt(0).toUpperCase();
    return '';
  }, [user]);

  const handleSignOut = () => {
    signOut();
    setCurrentPage('search');
  };

  return (
    <div className="bg-white border-b border-slate-200 px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-8">
          <button 
            onClick={() => setCurrentPage('search')}
            className="flex items-center gap-3 hover:bg-slate-50 rounded-lg p-2 transition-colors"
          >
            <div className="bg-gradient-to-r from-sky-500 to-indigo-500 rounded-lg p-2">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-800">CourseAI</h1>
              <p className="text-xs text-slate-500">스마트 강의 분석</p>
            </div>
          </button>
          
          <nav className="flex gap-1">
            {[
              { id: 'search', label: 'AI 강의 검색', icon: Search },
              { id: 'courses', label: '개설과목 현황', icon: List },
              { id: 'chat', label: 'AI 채팅', icon: MessageSquare },
              { id: 'gpa', label: '학점 계산', icon: Calculator }
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setCurrentPage(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    currentPage === tab.id 
                      ? 'bg-sky-50 text-sky-700 border border-sky-200' 
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <button className="p-2 text-slate-500 hover:text-slate-700 relative">
            <Bell className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
          </button>
          {user ? (
            <div className="flex items-center gap-3">
              <button 
                onClick={() => setCurrentPage('mypage')}
                className="flex items-center gap-3 hover:bg-slate-50 rounded-lg p-2 transition-colors"
              >
                {user.picture ? (
                  <img
                    src={user.picture}
                    alt={user.name || 'Google Account'}
                    className="w-8 h-8 rounded-full object-cover border border-slate-200"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <div className="w-8 h-8 bg-sky-500 rounded-full flex items-center justify-center text-white font-semibold">
                    {userInitial || <User className="w-5 h-5 text-white" />}
                  </div>
                )}
                <div className="text-left">
                  <p className="text-sm font-semibold text-slate-800">{displayName}</p>
                  <p className="text-xs text-slate-500">{displaySecondary}</p>
                </div>
              </button>
              <button
                onClick={handleSignOut}
                className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                로그아웃
              </button>
            </div>
          ) : (
            <GoogleSignInButton />
          )}
        </div>
      </div>
      {(loading || isAuthenticating) && (
        <div className="max-w-7xl mx-auto mt-2 text-xs text-slate-500">
          로그인 상태를 확인하고 있습니다...
        </div>
      )}
    </div>
  );
};

export default NavBar;
