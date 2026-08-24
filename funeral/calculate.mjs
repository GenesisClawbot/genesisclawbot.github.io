const CURRENCY_SYMBOLS = {
  GBP: '£',
  USD: '$',
  EUR: '€',
};

function parseMonthlyPrice(value) {
  const text = String(value ?? '').trim();
  if (/^\d+\.\d{3,}$/.test(text)) {
    throw new Error('Monthly price must use no more than two decimal places.');
  }
  if (!/^\d+(?:\.\d{1,2})?$/.test(text)) {
    throw new Error('Monthly price must be more than zero.');
  }

  const [whole, fraction = ''] = text.split('.');
  const minor = Number(whole) * 100 + Number(fraction.padEnd(2, '0'));
  if (!Number.isSafeInteger(minor)) throw new Error('Monthly price is too large.');
  if (minor <= 0) throw new Error('Monthly price must be more than zero.');
  return minor;
}

function parseWholeNumber(value, minimum, message) {
  const text = String(value ?? '').trim();
  if (!/^\d+$/.test(text)) throw new Error(message);
  const number = Number(text);
  if (!Number.isSafeInteger(number) || number < minimum) throw new Error(message);
  return number;
}

export function calculateAutopsy(input) {
  if (!Object.hasOwn(CURRENCY_SYMBOLS, input.currency)) {
    throw new Error('Choose GBP, USD, or EUR.');
  }

  const monthlyMinor = parseMonthlyPrice(input.monthlyPrice);
  const monthsPaid = parseWholeNumber(
    input.monthsPaid,
    1,
    'Months paid must be a whole number of at least one.',
  );
  const usefulSessions = parseWholeNumber(
    input.usefulSessions,
    0,
    'Useful sessions must be a whole number of zero or more.',
  );
  const totalMinor = monthlyMinor * monthsPaid;
  if (!Number.isSafeInteger(totalMinor)) {
    throw new Error('Months paid produces a total that is too large.');
  }

  return {
    service: String(input.service ?? '').trim() || 'Unnamed subscription',
    monthlyMinor,
    monthsPaid,
    usefulSessions,
    currency: input.currency,
    totalMinor,
    costPerUsefulSessionMinor: usefulSessions > 0
      ? Math.round(totalMinor / usefulSessions)
      : null,
  };
}

export function formatMoney(minor, currency) {
  const symbol = CURRENCY_SYMBOLS[currency];
  const amount = new Intl.NumberFormat('en-GB', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(minor / 100);
  return `${symbol}${amount}`;
}

export function receiptData(result) {
  const hasUsefulSessions = result.usefulSessions > 0;
  return {
    service: result.service,
    monthly: formatMoney(result.monthlyMinor, result.currency),
    months: String(result.monthsPaid),
    usefulSessions: String(result.usefulSessions),
    total: formatMoney(result.totalMinor, result.currency),
    each: hasUsefulSessions
      ? formatMoney(result.costPerUsefulSessionMinor, result.currency)
      : 'Not measurable',
    finding: hasUsefulSessions
      ? 'The corpse can explain itself.'
      : 'Division by zero has entered the chat.',
  };
}

export function shareText(result, url) {
  const total = formatMoney(result.totalMinor, result.currency);
  if (result.usefulSessions === 0) {
    return `Subscription autopsy: I paid ${total} and counted 0 useful sessions with ${result.service}. Division by zero has entered the chat. ${url}`;
  }

  const each = formatMoney(result.costPerUsefulSessionMinor, result.currency);
  return `Subscription autopsy: I paid ${total} for ${result.usefulSessions} useful sessions with ${result.service}. That is ${each} each. The corpse can explain itself. ${url}`;
}
