import { expect, test } from 'vitest';
import { sum } from '@/lib.js';
test('sum', () => { expect(sum(2,3)).toBe(5) });
