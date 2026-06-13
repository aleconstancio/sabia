import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

export type WithElementRef<T, E extends HTMLElement = HTMLElement> = Omit<T, 'ref'> & {
	ref?: E | null;
};

export type WithoutChildren<T> = Omit<T, 'children'>;

export type WithoutChild<T> = T & { children?: never };

export type WithoutChildrenOrChild<T> = WithoutChild<WithoutChildren<T>>;
