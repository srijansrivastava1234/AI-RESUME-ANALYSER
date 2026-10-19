import { describe, it, expect, vi } from 'vitest';
import { debounce, memoize, calculateKeywordDensity } from '../utils/performance';

describe('Performance Utilities', () => {
  describe('debounce', () => {
    it('should debounce rapid successive function calls', () => {
      vi.useFakeTimers();
      const fn = vi.fn();
      const debounced = debounce(fn, 200);

      debounced('a');
      debounced('b');
      debounced('c');

      expect(fn).not.toHaveBeenCalled();

      vi.advanceTimersByTime(199);
      expect(fn).not.toHaveBeenCalled();

      vi.advanceTimersByTime(1);
      expect(fn).toHaveBeenCalledTimes(1);
      expect(fn).toHaveBeenCalledWith('c');

      vi.useRealTimers();
    });
  });

  describe('memoize', () => {
    it('should cache results for identical arguments and avoid duplicate calls', () => {
      const expensiveCalc = vi.fn((x) => x * 2);
      const memoized = memoize(expensiveCalc);

      expect(memoized(5)).toBe(10);
      expect(expensiveCalc).toHaveBeenCalledTimes(1);

      expect(memoized(5)).toBe(10);
      expect(expensiveCalc).toHaveBeenCalledTimes(1);

      expect(memoized(10)).toBe(20);
      expect(expensiveCalc).toHaveBeenCalledTimes(2);
    });
  });

  describe('calculateKeywordDensity', () => {
    it('should return empty array for null, undefined or non-string input', () => {
      expect(calculateKeywordDensity(null)).toEqual([]);
      expect(calculateKeywordDensity(undefined)).toEqual([]);
      expect(calculateKeywordDensity(12345)).toEqual([]);
      expect(calculateKeywordDensity('')).toEqual([]);
    });

    it('should extract top keywords and filter default stopwords', () => {
      const text = 'Python Python Python Docker Docker Kubernetes and the for with is';
      const result = calculateKeywordDensity(text, 5);

      expect(result).toHaveLength(3);
      expect(result[0]).toEqual({ word: 'Python', count: 3 });
      expect(result[1]).toEqual({ word: 'Docker', count: 2 });
      expect(result[2]).toEqual({ word: 'Kubernetes', count: 1 });
    });

    it('should respect the limit parameter', () => {
      const text = 'React Vue Angular Svelte Next Nuxt Express Fastapi';
      const result = calculateKeywordDensity(text, 3);
      expect(result.length).toBeLessThanOrEqual(3);
    });
  });
});
