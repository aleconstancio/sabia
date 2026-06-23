import { logger } from '$lib/utils/logger';

export const API_URL = (() => {
  const url = import.meta.env.VITE_API_URL || '/api';
  if (import.meta.env.VITE_API_URL && !url.startsWith('http') && !url.startsWith('/')) {
    logger.warn(`VITE_API_URL="${url}" does not start with http or /. This may cause incorrect request URLs.`);
  }
  return url;
})();
