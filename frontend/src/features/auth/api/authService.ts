import { supabase } from '@/shared/api';
import type { User } from '@/entities/user';
import { GUEST_USER } from '@/entities/user';
import type { User as SupabaseUser } from '@supabase/supabase-js';

export function mapSupabaseUser(sbUser: SupabaseUser | null): User {
  if (!sbUser) return GUEST_USER;

  const metadata = sbUser.user_metadata || {};
  const name = metadata.full_name || metadata.name || sbUser.email?.split('@')[0] || '사용자';
  const avatarUrl = metadata.avatar_url || metadata.picture;
  const initials = name.slice(0, 2);

  return {
    id: sbUser.id,
    name,
    email: sbUser.email,
    avatarUrl,
    initials,
    isGuest: false,
  };
}

export async function signInWithGoogle(): Promise<{ error: Error | null }> {
  try {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin,
      },
    });
    return { error };
  } catch (err) {
    return { error: err instanceof Error ? err : new Error(String(err)) };
  }
}

export async function signOut(): Promise<{ error: Error | null }> {
  try {
    const { error } = await supabase.auth.signOut();
    return { error };
  } catch (err) {
    return { error: err instanceof Error ? err : new Error(String(err)) };
  }
}

export async function getCurrentUser(): Promise<User> {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    return mapSupabaseUser(session?.user ?? null);
  } catch (err) {
    console.error('Failed to get current auth session:', err);
    return GUEST_USER;
  }
}
