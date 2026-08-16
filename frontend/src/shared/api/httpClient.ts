export const httpClient = {
  delete: (url: string): Promise<Response> => fetch(url, { method: 'DELETE' }),
  post: <T>(url: string, body: T): Promise<Response> =>
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
};
