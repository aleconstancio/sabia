/**
 * Shared localStorage persistence utility for Svelte 5 rune stores.
 * 
 * Provides consistent load/persist/QuotaExceededError handling.
 */
import { logger } from '$lib/utils/logger';

export interface LocalStorageStore<T> {
  get data(): T[];
  set data(value: T[]);
  load(): void;
  persist(): void;
}

/**
 * Creates a localStorage-backed reactive store with Svelte 5 runes.
 * 
 * @param key - localStorage key
 * @param initial - initial value
 * @param options - configuration options
 * @returns Store object with data getter/setter, load, and persist methods
 */
export function createLocalStorageStore<T>(
  key: string,
  initial: T[] = [],
  options: { trimTo?: number; prefix?: string } = {}
): LocalStorageStore<T> {
  const { trimTo = 25, prefix = key } = options;
  let _data = $state<T[]>(initial);

  function load() {
    try {
      const raw = localStorage.getItem(key);
      const parsed = raw ? JSON.parse(raw) : [];
      _data = Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      logger.warn(`${prefix} load failed:`, e);
      _data = [];
    }
  }

  let _persistTimeout: ReturnType<typeof setTimeout> | undefined;

  function persist() {
    if (_persistTimeout) clearTimeout(_persistTimeout);
    _persistTimeout = setTimeout(() => {
      try {
        localStorage.setItem(key, JSON.stringify(_data));
      } catch (e) {
        if (e instanceof DOMException && e.name === 'QuotaExceededError') {
          logger.warn(`${prefix} localStorage quota exceeded, trimming old entries`);
          _data = _data.slice(0, trimTo);
          try {
            localStorage.setItem(key, JSON.stringify(_data));
          } catch (e: unknown) {
            logger.warn(`${prefix} give-up persist:`, e);
          }
        } else {
          logger.warn(`${prefix} persist failed:`, e);
        }
      }
    }, 100);
  }

  // Auto-load on creation
  load();

  return {
    get data() { return _data; },
    set data(value) { _data = value; persist(); },
    load,
    persist,
  };
}