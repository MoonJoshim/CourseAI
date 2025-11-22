import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, User } from 'lucide-react';

const MAJORS = [
  '소프트웨어학과',
  '컴퓨터공학과',
  'AI융합학과',
  '산업공학과',
];

const AuthForm = () => {
  const { signIn, signUp, updateProfile, isAuthenticating, authError } = useAuth();
  const [isSignUp, setIsSignUp] = useState(true); // 첫 화면은 회원가입 모드
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [major, setMajor] = useState(MAJORS[0]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isSignUp) {
        await signUp(email, password, major);
        if (major) {
          await updateProfile({ major });
        }
      } else {
        await signIn(email, password);
      }
    } catch {
      // 에러는 AuthContext에서 처리됨
    }
  };

  return (
    <div className="w-full max-w-md mx-auto bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-800 mb-6 text-center">
        {isSignUp ? '회원가입' : '로그인'}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1">
          <label className="text-sm text-slate-600 flex items-center gap-2">
            <Mail className="w-4 h-4" />
            이메일
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
            placeholder="example@email.com"
          />
        </div>

        <div className="space-y-1">
          <label className="text-sm text-slate-600 flex items-center gap-2">
            <Lock className="w-4 h-4" />
            비밀번호
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
            placeholder="비밀번호 입력"
            minLength={6}
          />
        </div>

        {isSignUp && (
          <div className="space-y-1">
            <label className="text-sm text-slate-600 flex items-center gap-2">
              <User className="w-4 h-4" />
              학과 선택
            </label>
            <select
              value={major}
              onChange={(e) => setMajor(e.target.value)}
              className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400 bg-white"
            >
              {MAJORS.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>
        )}

        {authError && (
          <p className="text-xs text-rose-500 text-center">{authError}</p>
        )}

        <button
          type="submit"
          disabled={isAuthenticating}
          className="w-full bg-sky-600 text-white py-2.5 rounded-lg font-medium hover:bg-sky-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAuthenticating ? '처리 중...' : isSignUp ? '가입하기' : '로그인'}
        </button>
      </form>

      <div className="mt-4 text-center">
        <button
          onClick={() => {
            setIsSignUp(!isSignUp);
          }}
          className="text-sm text-sky-600 hover:underline"
        >
          {isSignUp ? '이미 계정이 있으신가요? 로그인' : '계정이 없으신가요? 회원가입'}
        </button>
      </div>
    </div>
  );
};

export default AuthForm;

