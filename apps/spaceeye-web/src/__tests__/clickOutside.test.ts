import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the config module
vi.mock('$lib/config', () => ({
  API_URL: 'http://localhost:8000',
}));

describe('clickOutside', () => {
  let element: HTMLDivElement;

  beforeEach(() => {
    element = document.createElement('div');
    element.textContent = 'Test element';
    document.body.appendChild(element);
    
    return () => {
      document.body.removeChild(element);
    };
  });

  it('should export a function', async () => {
    const { clickOutside } = await import('$lib/actions/clickOutside');
    expect(typeof clickOutside).toBe('function');
  });

  it('should return update and destroy methods', async () => {
    const { clickOutside } = await import('$lib/actions/clickOutside');
    const handler = vi.fn();
    const result = clickOutside(element, { handler, enabled: true });
    
    expect(typeof result.update).toBe('function');
    expect(typeof result.destroy).toBe('function');
    
    result.destroy();
  });

  it('should call handler when clicking outside', async () => {
    const { clickOutside } = await import('$lib/actions/clickOutside');
    const handler = vi.fn();
    const result = clickOutside(element, { handler, enabled: true });
    
    // Click outside
    const outsideClick = new MouseEvent('mousedown', { bubbles: true });
    document.body.dispatchEvent(outsideClick);
    
    expect(handler).toHaveBeenCalled();
    
    result.destroy();
  });

  it('should not call handler when clicking inside', async () => {
    const { clickOutside } = await import('$lib/actions/clickOutside');
    const handler = vi.fn();
    const result = clickOutside(element, { handler, enabled: true });
    
    // Click inside
    const insideClick = new MouseEvent('mousedown', { bubbles: true });
    element.dispatchEvent(insideClick);
    
    expect(handler).not.toHaveBeenCalled();
    
    result.destroy();
  });

  it('should not call handler when disabled', async () => {
    const { clickOutside } = await import('$lib/actions/clickOutside');
    const handler = vi.fn();
    const result = clickOutside(element, { handler, enabled: false });
    
    // Click outside
    const outsideClick = new MouseEvent('mousedown', { bubbles: true });
    document.body.dispatchEvent(outsideClick);
    
    expect(handler).not.toHaveBeenCalled();
    
    result.destroy();
  });

  it('should not call handler when clicking on excluded element', async () => {
    const { clickOutside } = await import('$lib/actions/clickOutside');
    const handler = vi.fn();
    const excluded = document.createElement('button');
    document.body.appendChild(excluded);
    
    const result = clickOutside(element, { handler, enabled: true, exclude: [excluded] });
    
    // Click on excluded element
    const excludedClick = new MouseEvent('mousedown', { bubbles: true });
    excluded.dispatchEvent(excludedClick);
    
    expect(handler).not.toHaveBeenCalled();
    
    result.destroy();
    document.body.removeChild(excluded);
  });

  it('should support function shorthand', async () => {
    const { clickOutside } = await import('$lib/actions/clickOutside');
    const handler = vi.fn();
    const result = clickOutside(element, handler);
    
    // Click outside
    const outsideClick = new MouseEvent('mousedown', { bubbles: true });
    document.body.dispatchEvent(outsideClick);
    
    expect(handler).toHaveBeenCalled();
    
    result.destroy();
  });

  it('should clean up event listener on destroy', async () => {
    const { clickOutside } = await import('$lib/actions/clickOutside');
    const handler = vi.fn();
    const result = clickOutside(element, { handler, enabled: true });
    
    result.destroy();
    
    // Click outside - should not call handler after destroy
    const outsideClick = new MouseEvent('mousedown', { bubbles: true });
    document.body.dispatchEvent(outsideClick);
    
    expect(handler).not.toHaveBeenCalled();
  });

  it('should update options', async () => {
    const { clickOutside } = await import('$lib/actions/clickOutside');
    const handler = vi.fn();
    const result = clickOutside(element, { handler, enabled: true });
    
    // Disable
    result.update({ handler, enabled: false });
    
    // Click outside - should not call handler when disabled
    const outsideClick = new MouseEvent('mousedown', { bubbles: true });
    document.body.dispatchEvent(outsideClick);
    
    expect(handler).not.toHaveBeenCalled();
    
    result.destroy();
  });
});