import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

const USER_STORAGE_KEY = 'courseai.auth.user';
const USERS_STORAGE_KEY = 'courseai.auth.users';

const AuthContext = createContext({
  user: null,
  loading: false,
  isAuthenticating: false,
  authError: null,
  signIn: async () => {},
  signUp: async () => {},
  signOut: () => {},
  updateProfile: async () => {},
  setAuthError: () => {},
});

const loadStoredUsers = () => {
  if (typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(USERS_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.warn('Failed to parse stored users', error);
    return [];
  }
};

const saveStoredUsers = (users) => {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));
};

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

  const [loading, setLoading] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [authError, setAuthError] = useState(null);

  useEffect(() => {
    setLoading(false);
  }, []);

  const persistUser = useCallback((nextUser) => {
    if (typeof window === 'undefined') return;
    if (nextUser) {
      window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(nextUser));
    } else {
      window.localStorage.removeItem(USER_STORAGE_KEY);
    }
  }, []);

  const signOut = useCallback(() => {
    setUser(null);
    persistUser(null);
    setAuthError(null);
  }, [persistUser]);

  const signUp = useCallback(
    async (email, password, major) => {
      if (!email || !password) {
        setAuthError('이메일과 비밀번호를 입력해주세요.');
        return;
      }

      setIsAuthenticating(true);
      setAuthError(null);

      try {
        const normalizedEmail = String(email).trim().toLowerCase();
        const createdAt = new Date().toISOString();

        const allUsers = loadStoredUsers();
        if (allUsers.some((u) => u.email === normalizedEmail)) {
          throw new Error('이미 가입된 이메일입니다.');
        }

        const newUser = {
          id: `local-${Date.now()}`,
          email: normalizedEmail,
          password,
          createdAt,
          profile: {
            major: major || null,
          },
        };

        const nextUsers = [...allUsers, newUser];
        saveStoredUsers(nextUsers);

        setUser(newUser);
        persistUser(newUser);
      } catch (error) {
        console.error('Sign-up error', error);
        setAuthError(error.message);
        throw error;
      } finally {
        setIsAuthenticating(false);
      }
    },
    [persistUser]
  );

  const signIn = useCallback(
    async (email, password) => {
      if (!email || !password) {
        setAuthError('이메일과 비밀번호를 입력해주세요.');
        return;
      }

      setIsAuthenticating(true);
      setAuthError(null);

      try {
        const normalizedEmail = String(email).trim().toLowerCase();
        const allUsers = loadStoredUsers();
        const found = allUsers.find((u) => u.email === normalizedEmail);

        if (!found || found.password !== password) {
          throw new Error('이메일 또는 비밀번호가 올바르지 않습니다.');
        }

        setUser(found);
        persistUser(found);
      } catch (error) {
        console.error('Sign-in error', error);
        setAuthError(error.message);
        throw error;
      } finally {
        setIsAuthenticating(false);
      }
    },
    [persistUser]
  );

  const updateProfile = useCallback(
    async (profilePayload) => {
      if (!user) {
        throw new Error('로그인이 필요합니다.');
      }

      const nextUser = {
        ...user,
        profile: {
          ...(user.profile || {}),
          ...profilePayload,
        },
      };

      setUser(nextUser);
      persistUser(nextUser);

      const allUsers = loadStoredUsers().map((u) =>
        u.id === nextUser.id ? nextUser : u
      );
      saveStoredUsers(allUsers);

      return nextUser;
    },
    [user, persistUser]
  );

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticating,
      authError,
      setAuthError,
      signIn,
      signUp,
      signOut,
      updateProfile,
    }),
    [user, loading, isAuthenticating, authError, signIn, signUp, signOut, updateProfile]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

