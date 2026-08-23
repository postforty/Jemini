import { httpClient } from '@/shared/api';

export interface SubscriptionStatusResponse {
  user_id: string | null;
  plan_type: string;
  status: string;
  is_pro: boolean;
  current_period_end?: string | null;
}

export interface PaymentConfirmPayload {
  paymentKey: string;
  orderId: string;
  amount: number;
}

export async function confirmPayment(payload: PaymentConfirmPayload): Promise<SubscriptionStatusResponse> {
  const res = await httpClient.post<PaymentConfirmPayload>('/api/v1/payments/confirm', payload);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || '결제 승인 처리에 실패했습니다.');
  }
  return res.json();
}

export async function fetchSubscriptionStatus(): Promise<SubscriptionStatusResponse> {
  try {
    const res = await httpClient.get('/api/v1/payments/status');
    if (!res.ok) {
      return {
        user_id: null,
        plan_type: 'free',
        status: 'inactive',
        is_pro: false,
      };
    }
    return await res.json();
  } catch (error) {
    console.error('Failed to fetch subscription status:', error);
    return {
      user_id: null,
      plan_type: 'free',
      status: 'inactive',
      is_pro: false,
    };
  }
}
