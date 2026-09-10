/**
 * Performance utilities for the ATS Resume Analyser frontend.
 * Provides client-side memoization, debouncing, and optimized text frequency calculation.
 */

/**
 * Creates a debounced function that delays invoking `func` until after `wait` milliseconds
 * have elapsed since the last time the debounced function was invoked.
 *
 * @param {Function} func The function to debounce.
 * @param {number} wait The number of milliseconds to delay.
 * @returns {Function} Returns the new debounced function.
 */
export function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Simple memoization cache wrapper for single-argument functions.
 *
 * @param {Function} fn Function to memoize.
 * @returns {Function} Memoized function.
 */
export function memoize(fn) {
  const cache = new Map();
  return function (arg) {
    if (cache.has(arg)) {
      return cache.get(arg);
    }
    const result = fn(arg);
    cache.set(arg, result);
    return result;
  };
}

const DEFAULT_STOPWORDS = new Set([
  'the', 'and', 'a', 'of', 'to', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'i', 'you', 'it', 'he', 'she', 'they', 'we',
  'as', 'an', 'are', 'at', 'be', 'from', 'has', 'have', 'his', 'her', 'in', 'into', 'its', 'my', 'or', 'their', 'there', 'who', 'which',
  'was', 'were', 'will', 'with', 'about', 'but', 'not', 'can', 'our', 'out', 'all', 'more', 'some', 'any', 'been', 'other', 'than',
  'very', 'using', 'used', 'through', 'under', 'over', 'during', 'before', 'after', 'between', 'also', 'each', 'both', 'some'
]);

/**
 * Calculates top keyword frequency density from raw text, filtering common stopwords.
 *
 * @param {string} text Plain text of resume
 * @param {number} limit Number of top keywords to return
 * @returns {Array<{word: string, count: number}>} Top frequency keywords
 */
export function calculateKeywordDensity(text, limit = 10) {
  if (!text || typeof text !== 'string') return [];

  const words = text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .split(/\s+/)
    .filter(w => w.length > 2 && !DEFAULT_STOPWORDS.has(w));

  const freq = {};
  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    freq[w] = (freq[w] || 0) + 1;
  }

  return Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([word, count]) => ({
      word: word.charAt(0).toUpperCase() + word.slice(1),
      count
    }));
}
