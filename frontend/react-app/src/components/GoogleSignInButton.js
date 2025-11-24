import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';

const GoogleSignInButton = () => {
  const { signInWithGoogle, isAuthenticating, authError, setAuthError } = useAuth();
  const buttonRef = useRef(null);
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

  useEffect(() => {
    if (!clientId) {
      console.warn('REACT_APP_GOOGLE_CLIENT_ID가 설정되지 않았습니다.');
      return;
    }

    const renderButton = () => {
      if (!window.google?.accounts?.id || !buttonRef.current) return;

      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (response) => {
          if (!response.credential) {
            setAuthError('Google에서 유효한 토큰을 반환하지 않았습니다.');
            return;
          }
          signInWithGoogle(response.credential);
        },
        auto_select: false,
      });

      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: 'outline',
        size: 'medium',
        width: 200,
        shape: 'rectangular',
        text: 'signin_with',
      });
    };

    if (window.google?.accounts?.id) {
      renderButton();
      setScriptLoaded(true);
      return;
    }

    const existingScript = document.querySelector('script[data-google-accounts-script]');
    if (existingScript) {
      existingScript.addEventListener('load', renderButton);
      setScriptLoaded(true);
      return () => existingScript.removeEventListener('load', renderButton);
    }

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.dataset.googleAccountsScript = 'true';
    script.onload = () => {
      setScriptLoaded(true);
      renderButton();
    };
    script.onerror = () => {
      setAuthError('Google 로그인 스크립트를 불러오지 못했습니다.');
    };

    document.body.appendChild(script);

    return () => {
      script.onload = null;
      script.onerror = null;
    };
  }, [clientId, signInWithGoogle, setAuthError]);

  if (!clientId) {
    return (
      <div className="text-xs text-rose-500">
        Google Client ID가 설정되지 않았습니다.
      </div>
    );
  }

  return (
    <div className="flex flex-col items-end gap-2">
      <div
        ref={buttonRef}
        className={`flex items-center justify-center ${!scriptLoaded ? 'opacity-0 pointer-events-none' : 'opacity-100 transition-opacity duration-150'}`}
        aria-live="polite"
      />
      {isAuthenticating && (
        <p className="text-xs text-slate-500">Google 계정으로 로그인 중...</p>
      )}
      {authError && (
        <p className="text-xs text-rose-500 max-w-xs text-right">{authError}</p>
      )}
    </div>
  );
};

export default GoogleSignInButton;

