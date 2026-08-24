import { formatReceipt, parseTranscript } from './core.mjs';

const BOOT_ID = document.documentElement.dataset.build;
const BOOT_STORAGE_KEY = 'one-small-fix-boot-id';

function hardReload(nextBootId) {
  const url = new URL(window.location.href);
  if (url.searchParams.get('boot') === nextBootId) return;
  url.searchParams.set('boot', nextBootId);
  window.location.replace(url);
}

try {
  const latestBootId = window.localStorage.getItem(BOOT_STORAGE_KEY);
  if (latestBootId && latestBootId > BOOT_ID) {
    hardReload(latestBootId);
  } else if (!latestBootId || BOOT_ID > latestBootId) {
    window.localStorage.setItem(BOOT_STORAGE_KEY, BOOT_ID);
  }
} catch {
  // A blocked local store does not block transcript parsing.
}

window.addEventListener('storage', (event) => {
  if (event.key === BOOT_STORAGE_KEY && event.newValue > BOOT_ID) {
    hardReload(event.newValue);
  }
});

const loadedUrl = new URL(window.location.href);
if (loadedUrl.searchParams.get('boot') === BOOT_ID) {
  loadedUrl.searchParams.delete('boot');
  window.history.replaceState(null, '', loadedUrl);
}

const transcriptInput = document.querySelector('#transcript');
const dropzone = document.querySelector('#dropzone');
const receipt = document.querySelector('#receipt');
const receiptHeading = document.querySelector('#receipt-heading');
const receiptText = document.querySelector('#receipt-text');
const privacyCheck = document.querySelector('#privacy-check');
const copyButton = document.querySelector('#copy-button');
const saveButton = document.querySelector('#save-button');
const status = document.querySelector('#status');
const metricDuration = document.querySelector('#metric-duration');
const metricTools = document.querySelector('#metric-tools');
const metricWrites = document.querySelector('#metric-writes');
const metricTests = document.querySelector('#metric-tests');
const writeList = document.querySelector('#write-list');
const testList = document.querySelector('#test-list');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function formatDuration(milliseconds) {
  if (!Number.isFinite(milliseconds)) return 'Unknown';
  const totalSeconds = Math.max(0, Math.round(milliseconds / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  if (!minutes) return `${seconds}s`;
  return `${minutes}m ${seconds}s`;
}

function fillList(list, values, emptyText) {
  list.replaceChildren();
  const entries = values.length ? values : [emptyText];
  for (const value of entries) {
    const item = document.createElement('li');
    item.textContent = value;
    if (!values.length) item.className = 'empty-row';
    list.append(item);
  }
}

function lockActions() {
  privacyCheck.checked = false;
  copyButton.disabled = true;
  saveButton.disabled = true;
}

function hideReceipt() {
  receipt.hidden = true;
  lockActions();
}

function showReceipt(summary) {
  metricDuration.textContent = formatDuration(summary.elapsedMs);
  metricTools.textContent = String(summary.toolCalls);
  metricWrites.textContent = String(summary.filesWritten.length);
  metricTests.textContent = String(summary.testCommands.length);
  fillList(writeList, summary.filesWritten, 'None observed through direct write calls.');
  fillList(testList, summary.testCommands, 'None observed.');
  receiptText.value = formatReceipt(summary);
  lockActions();
  receipt.hidden = false;
  receiptHeading.focus();
  receipt.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
}

async function readTranscript(file) {
  if (!file) return;
  status.textContent = `Reading ${file.name} locally.`;
  try {
    const source = await file.text();
    const summary = parseTranscript(source);
    showReceipt(summary);
    status.textContent = 'Receipt ready. Read it before you copy or save it.';
  } catch (error) {
    hideReceipt();
    status.textContent = error instanceof Error ? error.message : 'This transcript could not be read.';
    transcriptInput.value = '';
    transcriptInput.focus();
  }
}

transcriptInput.addEventListener('change', () => {
  readTranscript(transcriptInput.files?.[0]);
});

for (const eventName of ['dragenter', 'dragover']) {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add('is-dragging');
  });
}

for (const eventName of ['dragleave', 'drop']) {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove('is-dragging');
  });
}

dropzone.addEventListener('drop', (event) => {
  readTranscript(event.dataTransfer?.files?.[0]);
});

privacyCheck.addEventListener('change', () => {
  copyButton.disabled = !privacyCheck.checked;
  saveButton.disabled = !privacyCheck.checked;
  status.textContent = privacyCheck.checked
    ? 'Receipt checked. Copy or save when ready.'
    : 'Read the receipt before you copy or save it.';
});

receiptText.addEventListener('input', () => {
  if (!privacyCheck.checked) return;
  lockActions();
  status.textContent = 'Receipt changed. Check it again before you copy or save it.';
});

copyButton.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(receiptText.value);
    status.textContent = 'Receipt copied.';
  } catch {
    status.textContent = 'Copy failed. Select the receipt text and copy it manually.';
    receiptText.focus();
    receiptText.select();
  }
});

saveButton.addEventListener('click', () => {
  const blob = new Blob([`${receiptText.value}\n`], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'one-small-fix-scope-receipt.txt';
  link.click();
  URL.revokeObjectURL(url);
  status.textContent = 'Receipt saved.';
});
