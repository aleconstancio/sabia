/**
 * Creates a typed API client with API key auth, JSON parsing, and error handling.
 *
 * Usage:
 * <script lang="ts">
 *   import { createApiClient } from '$lib/ui/utils/createApiClient';
 *
 *   const api = createApiClient({
 *     baseUrl: API_URL,
 *     getToken: () => localStorage.getItem('spaceeye_api_key'),
 *   });
 *
 *   const items = await api.get<Item[]>('/items');
 *   await api.post('/items/123', { name: 'test' });
 * </script>
 */

export interface ApiClientOptions {
  baseUrl: string;
  getToken?: () => string | null;
  onError?: (error: Error, path: string) => void;
}

export function createApiClient<TBase extends Record<string, (...args: unknown[]) => Promise<unknown>> = {}>(
  options: ApiClientOptions,
  domainApis?: TBase
) {
  const { baseUrl, getToken, onError } = options;

  async function request<T>(path: string, method: string = 'GET', body?: unknown): Promise<T> {
    const headers = new Headers();
    const apiKey = getToken?.();
    if (apiKey) headers.set('X-API-Key', apiKey);
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
    post<T>(path: string, body?: unknown): Promise<T> {
      return request<T>(path, 'POST', body);
    },
    put<T>(path: string, body?: unknown): Promise<T> {
      return request<T>(path, 'PUT', body);
    },
    patch<T>(path: string, body?: unknown): Promise<T> {
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
    /**
     * POST request that returns a Blob instead of JSON (for file downloads).
     */
    async postBlob(path: string, body?: unknown): Promise<Blob> {
      const headers = new Headers();
      const token = getToken?.();
      if (token) headers.set('X-API-Key', token);
      if (body && !(body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
      }

      const response = await fetch(`${baseUrl}${path}`, {
        method: 'POST',
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

      return response.blob();
    },
  };

  return Object.assign(client, domainApis || {});
}
