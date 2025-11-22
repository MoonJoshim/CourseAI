import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

const TOKEN_STORAGE_KEY = 'courseai.auth.token';
const USER_STORAGE_KEY = 'courseai.auth.user';

const defaultBackendUrl = () => {
  if (typeof window === 'undefined') {
    return 'http://34.58.143.2:5002';
  }
  return 'http://34.58.143.2:5002';
};

const AuthContext = createContext({
  user: null,
  token: null,
  backendUrl: '',
  loading: false,
  isAuthenticating: false,
  authError: null,
  signInWithGoogle: async () => {},
  signOut: () => {},
  updateProfile: async () => {},
  setAuthError: () => {},
});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    if (typeof window === 'undefined') return null;
    try {
      const stored = window.localStorage.getItem(USER_STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.warn('Failed to parse stored user info', error);
      return null;
    }
  });

  const [token, setToken] = useState(() => {
    if (typeof window === 'undefined') return null;
    return window.localStorage.getItem(TOKEN_STORAGE_KEY);
  });

  const [loading, setLoading] = useState(Boolean(token));
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [authError, setAuthError] = useState(null);

  const backendUrl = useMemo(() => {
    const fromEnv = process.env.REACT_APP_BACKEND_URL;
    if (fromEnv && fromEnv.trim()) {
      return fromEnv.replace(/\/$/, '');
    }
    return defaultBackendUrl();
  }, []);

  const persistAuthState = useCallback((nextToken, nextUser) => {
    if (typeof window === 'undefined') return;
    if (nextToken) {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, nextToken);
    } else {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    }

    if (nextUser) {
      window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(nextUser));
    } else {
      window.localStorage.removeItem(USER_STORAGE_KEY);
    }
  }, []);

  const resetAuthState = useCallback(() => {
    setUser(null);
    setToken(null);
    persistAuthState(null, null);
  }, [persistAuthState]);

  const signOut = useCallback(() => {
    resetAuthState();
    setAuthError(null);
    if (window.google?.accounts?.id) {
      window.google.accounts.id.disableAutoSelect();
    }
  }, [resetAuthState]);

  const fetchCurrentUser = useCallback(async (activeToken) => {
    if (!activeToken) {
      resetAuthState();
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${activeToken}`,
        },
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || '사용자 정보를 불러오지 못했습니다.');
      }

      setUser(data.user);
      persistAuthState(activeToken, data.user);
    } catch (error) {
      console.error('Failed to fetch current user', error);
      resetAuthState();
      setAuthError(error.message);
    } finally {
      setLoading(false);
    }
  }, [backendUrl, persistAuthState, resetAuthState]);

  useEffect(() => {
    if (token && !user) {
      setLoading(true);
      fetchCurrentUser(token);
    } else {
      setLoading(false);
    }
  }, [token, user, fetchCurrentUser]);

  const signInWithGoogle = useCallback(async (credential) => {
    if (!credential) {
      setAuthError('Google 인증 정보가 제공되지 않았습니다.');
      return;
    }

    setIsAuthenticating(true);
    setAuthError(null);

    try {
      const response = await fetch(`${backendUrl}/api/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ credential }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Google 로그인에 실패했습니다.');
      }

      setUser(data.user);
      setToken(data.token);
      persistAuthState(data.token, data.user);
    } catch (error) {
      console.error('Google sign-in error', error);
      setAuthError(error.message);
      resetAuthState();
      throw error;
    } finally {
      setIsAuthenticating(false);
    }
  }, [backendUrl, persistAuthState, resetAuthState]);

  const updateProfile = useCallback(async (profilePayload) => {
    if (!token) {
      throw new Error('로그인이 필요합니다.');
    }

    try {
      const response = await fetch(`${backendUrl}/api/users/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(profilePayload),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || '사용자 정보를 업데이트하지 못했습니다.');
      }

      setUser(data.user);
      persistAuthState(token, data.user);
      return data.user;
    } catch (error) {
      console.error('Failed to update profile', error);
      setAuthError(error.message);
      throw error;
    }
  }, [backendUrl, token, persistAuthState]);

  const value = useMemo(() => ({
    user,
    token,
    backendUrl,
    loading,
    isAuthenticating,
    authError,
    setAuthError,
    signInWithGoogle,
    signOut,
    updateProfile,
  }), [
    user,
    token,
    backendUrl,
    loading,
    isAuthenticating,
    authError,
    signInWithGoogle,
    signOut,
    updateProfile,
  ]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

