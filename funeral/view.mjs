export function announceStatus(element, message, schedule = queueMicrotask) {
  element.textContent = '';
  schedule(() => {
    element.textContent = message;
  });
}

export function showFormError(message, elements, schedule = queueMicrotask) {
  elements.section.hidden = true;
  elements.error.textContent = message;
  announceStatus(elements.status, `Could not complete autopsy. ${message}`, schedule);
  elements.field.focus();
}

export function showReceipt(data, elements, schedule = queueMicrotask) {
  elements.service.textContent = data.service;
  elements.monthly.textContent = data.monthly;
  elements.months.textContent = data.months;
  elements.usefulSessions.textContent = data.usefulSessions;
  elements.total.textContent = data.total;
  elements.each.textContent = data.each;
  elements.finding.textContent = data.finding;
  elements.section.hidden = false;
  announceStatus(elements.status, 'Autopsy complete. The receipt is ready.', schedule);
  elements.heading.focus();
}
