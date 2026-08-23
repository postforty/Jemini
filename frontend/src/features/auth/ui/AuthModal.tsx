import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useUserStore } from '@/entities/user';
import { signInWithGoogle } from '../api/authService';
import styles from './AuthModal.module.css';

export function AuthModal() {
  const isOpen = useUserStore((s) => s.isAuthModalOpen);
  const setOpen = useUserStore((s) => s.setAuthModalOpen);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleClose = () => {
    if (loading) return;
    setErrorMsg(null);
    setOpen(false);
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const { error } = await signInWithGoogle();
      if (error) {
        setErrorMsg(error.message || 'Google 로그인에 실패했습니다. 다시 시도해주세요.');
        setLoading(false);
      }
      // If successful, Supabase redirects to OAuth URL
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      setLoading(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={handleClose}>
      <div className={styles.modalCard} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={handleClose} title="닫기">
          <X size={18} />
        </button>

        <div className={styles.iconWrapper}>
          <svg className={styles.sparkIcon} viewBox="0 0 24 24">
            <path
              d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z"
              fill="url(#jemini-grad)"
            />
          </svg>
        </div>

        <h2 className={styles.title}>로그인 후 대화를 이어가세요</h2>
        <p className={styles.description}>
          게스트 세션은 최대 2회까지 질문이 가능합니다.{'\n'}
          Google 계정으로 로그인하여 제한 없이 대화를 나눠보세요.
        </p>

        <div className={styles.buttonGroup}>
          <button
            className={styles.googleBtn}
            onClick={handleGoogleLogin}
            disabled={loading}
          >
            <svg className={styles.googleIcon} viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>{loading ? 'Google 로그인 연결 중...' : 'Google 계정으로 계속하기'}</span>
          </button>
        </div>

        {errorMsg && <div className={styles.errorBanner}>{errorMsg}</div>}

        <p className={styles.footnote}>
          로그인 시 대화 내역이 안전하게 보관됩니다.
        </p>
      </div>
    </div>
  );
}
