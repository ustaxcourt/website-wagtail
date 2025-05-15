import { isPdf,  } from './link-handler';
import { describe, it, expect } from 'vitest'

describe('isPdf', () => {
    it('should return true when url is for a pdf, regardless of the hash', () => {
        expect(isPdf('http://example.com/test.pdf')).toBe(true);
        expect(isPdf('http://example.com/test.pdf#rule-10')).toBe(true);
    });
});
