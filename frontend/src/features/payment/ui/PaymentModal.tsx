import React, { useState } from 'react';
import { Sparkles, Check, X, ShieldCheck, Zap, Bot, Loader2, CreditCard } from 'lucide-react';
import { loadTossPayments } from '@tosspayments/tosspayments-sdk';
import { useUserStore } from '@/entities/user';
import { TOSS_CLIENT_KEY, PRO_PLAN_NAME, PRO_PLAN_PRICE, PRO_PLAN_DESC } from '@/shared/config';
import { confirmPayment } from '../api/paymentApi';
import styles from './PaymentModal.module.css';

interface PaymentModalProps {
  onSuccess?: (modelId?: string | null) => void;
}

export function PaymentModal({ onSuccess }: PaymentModalProps) {
  const isPaymentModalOpen = useUserStore((s) => s.isPaymentModalOpen);
  const targetProModel = useUserStore((s) => s.targetProModel);
  const setPaymentModalOpen = useUserStore((s) => s.setPaymentModalOpen);
  const setIsPro = useUserStore((s) => s.setIsPro);
  const user = useUserStore((s) => s.user);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isPaymentModalOpen) return null;

  const handleClose = () => {
    if (isLoading) return;
    setErrorMsg(null);
    setPaymentModalOpen(false, null);
  };

  // 1. Toss Payments SDK Checkout Flow
  const handleTossPayment = async () => {
    if (!TOSS_CLIENT_KEY) {
      setErrorMsg('토스페이먼츠 클라이언트 키(VITE_TOSS_CLIENT_KEY)가 설정되지 않았습니다. 개발/테스트용 즉시 승인을 이용하시거나 환경 변수를 설정해 주세요.');
      return;
    }
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const tossPayments = await loadTossPayments(TOSS_CLIENT_KEY);
      const customerKey = user.id && user.id !== 'guest'
        ? `user_${user.id.replace(/-/g, '_')}`
        : `guest_${Date.now()}_test`;

      const payment = tossPayments.payment({ customerKey });
      const orderId = `order_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;

      await payment.requestPayment({
        method: 'CARD',
        amount: {
          currency: 'KRW',
          value: PRO_PLAN_PRICE,
        },
        orderId,
        orderName: PRO_PLAN_NAME,
        customerName: user.name || 'Jemini 사용자',
        customerEmail: user.email,
        successUrl: `${window.location.origin}/?payment_success=true&orderId=${orderId}`,
        failUrl: `${window.location.origin}/?payment_fail=true`,
      });
    } catch (err: any) {
      console.error('Toss Payments Error:', err);
      // If user cancelled the popup
      if (err?.code === 'USER_CANCEL' || err?.message?.includes('취소')) {
        setIsLoading(false);
        return;
      }
      setErrorMsg(err?.message || '토스페이먼츠 결제창을 여는 중 오류가 발생했습니다.');
      setIsLoading(false);
    }
  };


  // 2. Direct Test Payment (Instant Pro Approval for development & fast verification)
  const handleTestInstantPayment = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const testPaymentKey = `test_pk_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
      const testOrderId = `order_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;

      await confirmPayment({
        paymentKey: testPaymentKey,
        orderId: testOrderId,
        amount: PRO_PLAN_PRICE,
      });

      setIsPro(true);
      const chosenModel = targetProModel;
      handleClose();
      onSuccess?.(chosenModel);
    } catch (err: any) {
      console.error('Instant test payment confirmation error:', err);
      setErrorMsg(err.message || '결제 승인 처리 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={handleClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <div className={styles.headerContent}>
            <span className={styles.badge}>
              <Sparkles size={13} />
              Jemini PRO
            </span>
            <h2 className={styles.title}>Pro 멤버십 업그레이드</h2>
            <p className={styles.subtitle}>{PRO_PLAN_DESC}</p>
          </div>
          <button className={styles.closeBtn} onClick={handleClose} disabled={isLoading}>
            <X size={20} />
          </button>
        </div>

        <div className={styles.body}>
          {targetProModel && (
            <div className={styles.targetModelBanner}>
              <Bot size={18} />
              <span>
                선택하신 <span className={styles.targetModelName}>{targetProModel}</span> 모델을 사용하려면 Pro 멤버십이 필요합니다.
              </span>
            </div>
          )}

          <div className={styles.featuresList}>
            <div className={styles.featureItem}>
              <Check size={18} className={styles.featureIcon} />
              <span>Gemini 3.5, GPT-4o, Claude 3.5 Sonnet 등 프리미엄 모델 무제한</span>
            </div>
            <div className={styles.featureItem}>
              <Zap size={18} className={styles.featureIcon} />
              <span>대기열 없는 초고속 실시간 스트리밍 답변</span>
            </div>
            <div className={styles.featureItem}>
              <ShieldCheck size={18} className={styles.featureIcon} />
              <span>토스페이먼츠 안전 결제 & 언제든 자유롭게 해지 가능</span>
            </div>
          </div>

          <div className={styles.priceCard}>
            <span className={styles.priceLabel}>이용 요금</span>
            <div className={styles.priceValueWrapper}>
              <span className={styles.priceValue}>{PRO_PLAN_PRICE.toLocaleString()}원</span>
              <span className={styles.pricePeriod}>/ 월</span>
            </div>
          </div>

          {errorMsg && <div className={styles.errorBox}>{errorMsg}</div>}

          <div className={styles.actions}>
            <button
              className={styles.tossPayBtn}
              onClick={handleTossPayment}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  <span>결제 진행 중...</span>
                </>
              ) : (
                <>
                  <CreditCard size={18} />
                  <span>토스페이먼츠로 결제하기</span>
                </>
              )}
            </button>

            <button
              className={styles.testPayBtn}
              onClick={handleTestInstantPayment}
              disabled={isLoading}
            >
              ⚡ 개발/테스트용 즉시 승인 (Mock Payment)
            </button>
          </div>

          <p className={styles.footerNote}>
            결제 정보는 토스페이먼츠를 통해 안전하게 암호화되어 전송됩니다.
          </p>
        </div>
      </div>
    </div>
  );
}
