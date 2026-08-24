import test from 'node:test';
import assert from 'node:assert/strict';

const implementation = await import('./view.mjs').catch(() => ({}));
const { announceStatus, showFormError, showReceipt } = implementation;

test('re-announces the same status message', () => {
  const element = { textContent: 'Receipt copied.' };
  const scheduled = [];

  announceStatus?.(element, 'Receipt copied.', (work) => scheduled.push(work));

  assert.equal(element.textContent, '');
  assert.equal(scheduled.length, 1);
  scheduled[0]();
  assert.equal(element.textContent, 'Receipt copied.');
});

test('hides a stale receipt and focuses the invalid field', () => {
  const focused = [];
  const elements = {
    section: { hidden: false },
    error: {},
    status: {},
    field: { focus: () => focused.push('field') },
  };

  showFormError?.('Monthly price is invalid.', elements, (work) => work());

  assert.equal(elements.section.hidden, true);
  assert.equal(elements.error.textContent, 'Monthly price is invalid.');
  assert.equal(elements.status.textContent, 'Could not complete autopsy. Monthly price is invalid.');
  assert.deepEqual(focused, ['field']);
});

test('renders every receipt value and focuses the result heading', () => {
  const focused = [];
  const elements = {
    section: { hidden: true },
    heading: { focus: () => focused.push('heading') },
    service: {},
    monthly: {},
    months: {},
    usefulSessions: {},
    total: {},
    each: {},
    finding: {},
    status: {},
  };

  showReceipt?.({
    service: 'My coding tool',
    monthly: '£20.00',
    months: '3',
    usefulSessions: '4',
    total: '£60.00',
    each: '£15.00',
    finding: 'The corpse can explain itself.',
  }, elements, (work) => work());

  assert.equal(elements.section.hidden, false);
  assert.equal(elements.service.textContent, 'My coding tool');
  assert.equal(elements.monthly.textContent, '£20.00');
  assert.equal(elements.months.textContent, '3');
  assert.equal(elements.usefulSessions.textContent, '4');
  assert.equal(elements.total.textContent, '£60.00');
  assert.equal(elements.each.textContent, '£15.00');
  assert.equal(elements.finding.textContent, 'The corpse can explain itself.');
  assert.equal(elements.status.textContent, 'Autopsy complete. The receipt is ready.');
  assert.deepEqual(focused, ['heading']);
});
