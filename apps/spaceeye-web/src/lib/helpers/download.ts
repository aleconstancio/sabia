/**
 * Trigger a browser download from a Blob, cleaning up afterwards.
 */
function triggerDownload(blob: Blob, filename: string) {
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
 * Download a file from a URL by fetching it as a blob.
 */
export async function downloadBlob(url: string, filename: string, options?: RequestInit): Promise<void> {
  const resp = await fetch(url, options);
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
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    throw new Error(`Download failed: ${resp.status}`);
  }
  const blob = await resp.blob();
  triggerDownload(blob, filename);
}
