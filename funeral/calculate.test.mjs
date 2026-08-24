import test from 'node:test';
import assert from 'node:assert/strict';

const implementation = await import('./calculate.mjs').catch(() => ({}));
const { calculateAutopsy, formatMoney, receiptData, shareText } = implementation;

test('calculates total spend and per-session cost in minor units', () => {
  const result = calculateAutopsy?.({
    service: '  Claude Max  ',
    monthlyPrice: '19.99',
    monthsPaid: '3',
    usefulSessions: '4',
    currency: 'GBP',
  });

  assert.deepEqual(result, {
    service: 'Claude Max',
    monthlyMinor: 1999,
    monthsPaid: 3,
    usefulSessions: 4,
    currency: 'GBP',
    totalMinor: 5997,
    costPerUsefulSessionMinor: 1499,
  });
});

test('keeps zero useful sessions finite', () => {
  const result = calculateAutopsy?.({
    service: '',
    monthlyPrice: '20',
    monthsPaid: '2',
    usefulSessions: '0',
    currency: 'USD',
  });

  assert.equal(result.service, 'Unnamed subscription');
  assert.equal(result.totalMinor, 4000);
  assert.equal(result.costPerUsefulSessionMinor, null);
});

test('rejects malformed or impossible inputs', () => {
  const cases = [
    [{ monthlyPrice: '0', monthsPaid: '1', usefulSessions: '1', currency: 'GBP' }, 'Monthly price must be more than zero.'],
    [{ monthlyPrice: '3.999', monthsPaid: '1', usefulSessions: '1', currency: 'GBP' }, 'Monthly price must use no more than two decimal places.'],
    [{ monthlyPrice: '10', monthsPaid: '1.5', usefulSessions: '1', currency: 'GBP' }, 'Months paid must be a whole number of at least one.'],
    [{ monthlyPrice: '10', monthsPaid: '1', usefulSessions: '-1', currency: 'GBP' }, 'Useful sessions must be a whole number of zero or more.'],
    [{ monthlyPrice: '10', monthsPaid: '1', usefulSessions: '1', currency: 'JPY' }, 'Choose GBP, USD, or EUR.'],
  ];

  for (const [input, message] of cases) {
    assert.throws(() => calculateAutopsy?.(input), { message });
  }
});

test('rejects amounts outside exact minor-unit arithmetic', () => {
  assert.throws(
    () => calculateAutopsy?.({
      monthlyPrice: '90071992547409.92',
      monthsPaid: '1',
      usefulSessions: '1',
      currency: 'GBP',
    }),
    { message: 'Monthly price is too large.' },
  );

  assert.throws(
    () => calculateAutopsy?.({
      monthlyPrice: '90071992547409.91',
      monthsPaid: '2',
      usefulSessions: '1',
      currency: 'GBP',
    }),
    { message: 'Months paid produces a total that is too large.' },
  );
});

test('formats supported currencies with two decimal places', () => {
  assert.equal(formatMoney?.(1299, 'GBP'), '£12.99');
  assert.equal(formatMoney?.(1299, 'USD'), '$12.99');
  assert.equal(formatMoney?.(1299, 'EUR'), '€12.99');
});

test('formats receipt fields for the visible result', () => {
  const result = calculateAutopsy?.({
    service: 'My coding tool',
    monthlyPrice: '20',
    monthsPaid: '3',
    usefulSessions: '4',
    currency: 'GBP',
  });

  assert.deepEqual(receiptData?.(result), {
    service: 'My coding tool',
    monthly: '£20.00',
    months: '3',
    usefulSessions: '4',
    total: '£60.00',
    each: '£15.00',
    finding: 'The corpse can explain itself.',
  });
});

test('uses a finite receipt message for zero useful sessions', () => {
  const result = calculateAutopsy?.({
    service: 'My coding tool',
    monthlyPrice: '20',
    monthsPaid: '3',
    usefulSessions: '0',
    currency: 'GBP',
  });

  assert.equal(receiptData?.(result).each, 'Not measurable');
  assert.equal(receiptData?.(result).finding, 'Division by zero has entered the chat.');
});

test('writes a factual share line from the entered numbers', () => {
  const result = calculateAutopsy?.({
    service: 'My coding tool',
    monthlyPrice: '20',
    monthsPaid: '3',
    usefulSessions: '4',
    currency: 'GBP',
  });

  assert.equal(
    shareText?.(result, 'https://jamiecole.page/funeral/'),
    'Subscription autopsy: I paid £60.00 for 4 useful sessions with My coding tool. That is £15.00 each. The corpse can explain itself. https://jamiecole.page/funeral/',
  );
});

test('does not divide by zero in shared copy', () => {
  const result = calculateAutopsy?.({
    service: 'My coding tool',
    monthlyPrice: '20',
    monthsPaid: '3',
    usefulSessions: '0',
    currency: 'GBP',
  });

  assert.equal(
    shareText?.(result, 'https://jamiecole.page/funeral/'),
    'Subscription autopsy: I paid £60.00 and counted 0 useful sessions with My coding tool. Division by zero has entered the chat. https://jamiecole.page/funeral/',
  );
});
