import { API_URL } from '$lib/config';

/**
 * Trigger a browser download from a Blob, cleaning up afterwards.
 */
export function triggerDownload(blob: Blob, filename: string) {
  const blobUrl = URL.createObjectURL(blob);
  const a = document.createElement('a');
  try {
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
  } finally {
    document.body.removeChild(a);
    URL.revokeObjectURL(blobUrl);
  }
}

/**
 * Get auth headers for download requests.
 * Uses X-API-Key header consistent with the backend auth middleware.
 */
function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  if (typeof localStorage !== 'undefined') {
    const apiKey = localStorage.getItem('sabia_api_key');
    if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }
  }
  return headers;
}

/**
 * Download a file from a URL by fetching it as a blob.
 */
export async function downloadBlob(url: string, filename: string, options?: RequestInit): Promise<void> {
  const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`;
  const resp = await fetch(fullUrl, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options?.headers,
    },
  });
  if (!resp.ok) {
    throw new Error(`Download failed: ${resp.status}`);
  }
  const blob = await resp.blob();
  triggerDownload(blob, filename);
}

/**
 * Download a file by POSTing JSON and receiving a blob.
 */
export async function downloadBlobPost(url: string, body: unknown, filename: string): Promise<void> {
  const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`;
  const resp = await fetch(fullUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    throw new Error(`Download failed: ${resp.status}`);
  }
  const blob = await resp.blob();
  triggerDownload(blob, filename);
}