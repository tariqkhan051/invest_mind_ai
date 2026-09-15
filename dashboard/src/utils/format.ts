export function formatCurrency(value: string | number | null | undefined, currency = "PKR") {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return "—";
  }
  return `${currency} ${amount.toLocaleString(undefined, {
    maximumFractionDigits: 0,
  })}`;
}

export function formatPercent(value: string | number | null | undefined, digits = 2) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return "—";
  }
  return `${amount.toFixed(digits)}%`;
}

export function formatNumber(value: string | number | null | undefined, digits = 2) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return "—";
  }
  return amount.toLocaleString(undefined, {
    maximumFractionDigits: digits,
  });
}

export function formatDate(value: string | null | undefined) {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
