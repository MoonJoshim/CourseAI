import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, User } from 'lucide-react';
import { MAJORS } from '../constants/majors';

const AuthForm = () => {
  const { signIn, signUp, updateProfile, isAuthenticating, authError } = useAuth();
  const [isSignUp, setIsSignUp] = useState(true);
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
    <div className="w-full max-w-md mx-auto bg-white border rounded-lg p-6 shadow-sm" style={{borderColor: '#B6CFB6'}}>
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
            className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2"
            style={{borderColor: '#B6CFB6'}}
            onFocus={(e) => e.target.style.borderColor = '#8FCACA'}
            onBlur={(e) => e.target.style.borderColor = '#B6CFB6'}
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
            className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2"
            style={{borderColor: '#B6CFB6'}}
            onFocus={(e) => e.target.style.borderColor = '#8FCACA'}
            onBlur={(e) => e.target.style.borderColor = '#B6CFB6'}
            placeholder="비밀번호 입력"
            minLength={6}
          />
        </div>

        {isSignUp && (
          <div className="space-y-1">
            <label className="text-sm text-slate-600 flex items-center gap-2">
              <User className="w-4 h-4" />
              전공 선택
            </label>
            <select
              value={major}
              onChange={(e) => setMajor(e.target.value)}
              required
              className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2"
              style={{borderColor: '#B6CFB6'}}
              onFocus={(e) => e.target.style.borderColor = '#8FCACA'}
              onBlur={(e) => e.target.style.borderColor = '#B6CFB6'}
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
          <div className="p-3 rounded text-sm" style={{backgroundColor: '#FFE6E6', color: '#DC2626'}}>
            {authError}
          </div>
        )}

        <button
          type="submit"
          disabled={isAuthenticating}
          className="w-full py-2.5 text-white rounded-lg font-medium transition-all text-sm shadow-sm disabled:opacity-50"
          style={{background: 'linear-gradient(to right, #8FCACA, #97C1A9)'}}
          onMouseEnter={(e) => {
            if (!e.target.disabled) {
              e.target.style.background = 'linear-gradient(to right, #7AB8B8, #86B098)';
            }
          }}
          onMouseLeave={(e) => {
            if (!e.target.disabled) {
              e.target.style.background = 'linear-gradient(to right, #8FCACA, #97C1A9)';
            }
          }}
        >
          {isAuthenticating ? '처리 중...' : isSignUp ? '가입하기' : '로그인'}
        </button>
      </form>

      <div className="mt-6 text-center">
        <button
          onClick={() => setIsSignUp(!isSignUp)}
          className="text-sm text-slate-600 hover:text-slate-900 underline"
        >
          {isSignUp ? '이미 계정이 있으신가요? 로그인' : '계정이 없으신가요? 회원가입'}
        </button>
      </div>
    </div>
  );
};

export default AuthForm;
