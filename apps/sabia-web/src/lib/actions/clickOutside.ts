/**
 * Svelte action for handling click-outside events.
 * 
 * Usage:
 *   <div use:clickOutside={() => isOpen = false}>
 *     Content
 *   </div>
 * 
 * Or with options:
 *   <div use:clickOutside={{ handler: () => isOpen = false, enabled: isOpen }}>
 *     Content
 *   </div>
 */
import type { Action, ActionReturn } from 'svelte/action';

export interface ClickOutsideOptions {
  /** Callback when a click occurs outside the element */
  handler: (event: MouseEvent) => void;
  /** Whether the action is enabled (default: true) */
  enabled?: boolean;
  /** Elements to exclude from triggering the handler (e.g., trigger button) */
  exclude?: HTMLElement[];
}

/**
 * Svelte action that detects clicks outside the target element.
 * 
 * @param node - The DOM element to monitor
 * @param options - Configuration options
 * @returns ActionReturn with update and destroy methods
 */
export const clickOutside: Action<HTMLElement, ClickOutsideOptions | ((event: MouseEvent) => void)> = (
  node: HTMLElement,
  options: ClickOutsideOptions | ((event: MouseEvent) => void) | undefined = undefined
): ActionReturn<ClickOutsideOptions | ((event: MouseEvent) => void)> => {
  const getOptions = (opts: ClickOutsideOptions | ((event: MouseEvent) => void) | undefined): ClickOutsideOptions => {
    if (!opts) {
      return { handler: () => {}, enabled: true };
    }
    if (typeof opts === 'function') {
      return { handler: opts, enabled: true };
    }
    return { enabled: true, ...opts };
  };

  let currentOptions = getOptions(options);

  const handleClick = (event: MouseEvent) => {
    if (!currentOptions.enabled) return;
    
    const target = event.target as Node;
    
    // Don't trigger if clicking inside the node
    if (node.contains(target)) return;
    
    // Don't trigger if clicking on excluded elements
    if (currentOptions.exclude?.some(el => el.contains(target))) return;
    
    currentOptions.handler(event);
  };

  // Use mousedown for more responsive feel (before click)
  document.addEventListener('mousedown', handleClick);

  return {
    update(newOptions: ClickOutsideOptions | ((event: MouseEvent) => void)) {
      currentOptions = getOptions(newOptions);
    },
    destroy() {
      document.removeEventListener('mousedown', handleClick);
    },
  };
};