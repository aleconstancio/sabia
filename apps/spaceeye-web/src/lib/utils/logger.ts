const isDev = import.meta.env.DEV;

function noop() {}

function createLogger(prefix: string) {
  return {
    debug: isDev ? (...args: unknown[]) => console.debug(`[${prefix}]`, ...args) : noop,
    warn: (...args: unknown[]) => console.warn(`[${prefix}]`, ...args),
    error: (...args: unknown[]) => console.error(`[${prefix}]`, ...args),
  };
}

export const logger = createLogger('SpaceEye');
