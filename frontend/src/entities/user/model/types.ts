export interface User {
  id: string;
  name: string;
  email?: string;
  avatarUrl?: string;
  initials: string;
  isGuest: boolean;
}

export const GUEST_USER: User = {
  id: 'guest',
  name: '게스트',
  initials: 'G',
  isGuest: true,
};
