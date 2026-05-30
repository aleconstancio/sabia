export type QueryStatus = 'loading' | 'success' | 'error';
export type FetchStatus = 'idle' | 'fetching';

interface CacheEntry<TData = unknown> {
  key: string;
  data: TData | undefined;
  error: Error | null;
  status: QueryStatus;
  fetchStatus: FetchStatus;
  lastUpdatedAt: number;
  promise: Promise<void> | null;
  subscribers: Set<() => void>;
  gcTimeout: ReturnType<typeof setTimeout> | null;
}

const cache = new Map<string, CacheEntry>();

function createEntry(key: string): CacheEntry {
  return {
    key,
    data: undefined,
    error: null,
    status: 'loading',
    fetchStatus: 'idle',
    lastUpdatedAt: 0,
    promise: null,
    subscribers: new Set(),
    gcTimeout: null,
  };
}

export function getEntry<T = unknown>(key: string): CacheEntry<T> | undefined {
  return cache.get(key) as CacheEntry<T> | undefined;
}

export function getOrCreateEntry<T = unknown>(key: string): CacheEntry<T> {
  let entry = cache.get(key);
  if (!entry) {
    entry = createEntry(key);
    cache.set(key, entry);
  }
  return entry as CacheEntry<T>;
}

export function subscribe(key: string, listener: () => void): () => void {
  const entry = getOrCreateEntry(key);
  entry.subscribers.add(listener);

  if (entry.gcTimeout) {
    clearTimeout(entry.gcTimeout);
    entry.gcTimeout = null;
  }

  return () => {
    entry.subscribers.delete(listener);
  };
}

export function notify(entry: CacheEntry): void {
  entry.subscribers.forEach(fn => fn());
}

export function defaultRetryDelay(attempt: number): number {
  return Math.min(1000 * 2 ** attempt, 30000);
}

export async function fetchQuery<T>(
  key: string,
  fetcher: () => Promise<T>,
  options?: { retry?: number }
): Promise<void> {
  const entry = getOrCreateEntry<T>(key);

  if (entry.promise) {
    return entry.promise;
  }

  entry.status = 'loading';
  entry.fetchStatus = 'fetching';
  entry.error = null;
  notify(entry);

  const maxRetries = options?.retry ?? 3;

  const promise = (async () => {
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const result = await fetcher();
        entry.data = result as any;
        entry.status = 'success';
        entry.fetchStatus = 'idle';
        entry.lastUpdatedAt = Date.now();
        entry.error = null;
        entry.promise = null;
        notify(entry);
        return;
      } catch (err) {
        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, defaultRetryDelay(attempt)));
        } else {
          entry.error = err instanceof Error ? err : new Error(String(err));
          entry.status = 'error';
          entry.fetchStatus = 'idle';
          entry.promise = null;
          notify(entry);
          return;
        }
      }
    }
  })();

  entry.promise = promise;
  return promise;
}

export function invalidateQuery(key: string): void {
  const entry = getEntry(key);
  if (!entry) return;
  entry.lastUpdatedAt = 0;
  notify(entry);
}

export function setQueryData<T>(key: string, data: T): void {
  const entry = getOrCreateEntry<T>(key);
  entry.data = data as any;
  entry.status = 'success';
  entry.lastUpdatedAt = Date.now();
  notify(entry);
}

export function removeEntry(key: string): void {
  const entry = cache.get(key);
  if (entry?.gcTimeout) {
    clearTimeout(entry.gcTimeout);
  }
  cache.delete(key);
}
