import { supabase } from './supabaseClient';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');

function formatUrl(url: string): string {
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  const normalizedPath = url.startsWith('/') ? url : `/${url}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      return { Authorization: `Bearer ${session.access_token}` };
    }
  } catch (err) {
    console.error('Failed to get auth session for request:', err);
  }
  return {};
}

export const httpClient = {
  get: async (url: string): Promise<Response> => {
    const authHeaders = await getAuthHeaders();
    return fetch(formatUrl(url), { method: 'GET', headers: { ...authHeaders } });
  },
  delete: async (url: string): Promise<Response> => {
    const authHeaders = await getAuthHeaders();
    return fetch(formatUrl(url), { method: 'DELETE', headers: { ...authHeaders } });
  },
  post: async <T>(url: string, body: T): Promise<Response> => {
    const authHeaders = await getAuthHeaders();
    return fetch(formatUrl(url), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
      },
      body: JSON.stringify(body),
    });
  },
};

