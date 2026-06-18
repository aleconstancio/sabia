export function getNdviColor(ndvi: number | null): string {
  if (ndvi == null) return '#6b7280';
  if (ndvi > 0.5) return '#10b981';
  if (ndvi > 0.3) return '#eab308';
  return '#ef4444';
}

export function formatTimeAgo(date: string | null): string {
  if (!date) return '';
  const diff = Date.now() - new Date(date).getTime();
  const secs = Math.floor(diff / 1000);
  if (secs < 60) return 'just now';
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function buildCsvExport(profiles: Array<Record<string, unknown>>, headers: string[], rows: string[][]): string {
  return [headers, ...rows].map(r => r.join(',')).join('\n');
}

export function downloadCsv(csv: string, filename: string) {
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
