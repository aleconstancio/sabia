import { pt } from './pt';
import { en } from './en';
import type { Translations } from './pt';

export type Locale = 'pt' | 'en';

const translations: Record<Locale, Translations> = { pt, en };

let _locale: Locale = 'pt';

export function setLocale(locale: Locale): void {
  _locale = locale;
  if (typeof window !== 'undefined') {
    localStorage.setItem('spaceeye_locale', locale);
  }
}

export function getLocale(): Locale {
  return _locale;
}

export function t(): Translations {
  return translations[_locale];
}

export function initLocale(): void {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('spaceeye_locale') as Locale | null;
    if (stored && (stored === 'pt' || stored === 'en')) {
      _locale = stored;
    }
  }
}
