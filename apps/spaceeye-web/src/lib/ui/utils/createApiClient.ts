/**
 * Creates a typed API client with Bearer token auth, JSON parsing, and error handling.
 *
 * Usage:
 * <script lang="ts">
 *   import { createApiClient } from '@thoth/ui';
 *
 *   const api = createApiClient('/api/v1', {
 *     getToken: () => localStorage.getItem('token'),
 *   });
 *
 *   const items = await api.get<Item[]>('/items', { state: 'pending' });
 *   await api.post('/items/123/transition', { state: 'approved' });
 * </script>
 */

export interface ApiClientOptions {
  baseUrl: string;
  getToken?: () => string | null;
  onError?: (error: Error, path: string) => void;
}

export function createApiClient<TBase extends Record<string, (...args: any[]) => Promise<any>> = {}>(
  options: ApiClientOptions,
  domainApis?: TBase
) {
  const { baseUrl, getToken, onError } = options;

  async function request<T>(path: string, method: string = 'GET', body?: any): Promise<T> {
    const headers = new Headers();
    const token = getToken?.();
    if (token) headers.set('Authorization', `Bearer ${token}`);
    if (body && !(body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(`${baseUrl}${path}`, {
      method,
      headers,
      credentials: 'same-origin',
      body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: `HTTP ${response.status}` }));
      const error = new Error(errorData.message || errorData.code || `HTTP ${response.status}`);
      onError?.(error, path);
      throw error;
    }

    if (response.status === 204) return {} as T;
    return response.json();
  }

  const client = {
    get<T>(path: string, params?: Record<string, string>): Promise<T> {
      const qs = params ? '?' + new URLSearchParams(params).toString() : '';
      return request<T>(`${path}${qs}`, 'GET');
    },
    post<T>(path: string, body?: any): Promise<T> {
      return request<T>(path, 'POST', body);
    },
    put<T>(path: string, body?: any): Promise<T> {
      return request<T>(path, 'PUT', body);
    },
    patch<T>(path: string, body?: any): Promise<T> {
      return request<T>(path, 'PATCH', body);
    },
    delete<T>(path: string): Promise<T> {
      return request<T>(path, 'DELETE');
    },
    upload<T>(path: string, file: File, extraData?: Record<string, string>): Promise<T> {
      const formData = new FormData();
      formData.append('file', file);
      if (extraData) {
        Object.entries(extraData).forEach(([k, v]) => formData.append(k, v));
      }
      return request<T>(path, 'POST', formData);
    },
  };

  return Object.assign(client, domainApis || {});
}
