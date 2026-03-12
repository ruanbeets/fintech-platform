// src/utils/currencyUtils.js

export function getUserCurrency() {

  return localStorage.getItem("currency") || "USD";

}

export function formatCurrency(value, currency = null) {

  const selectedCurrency = currency || getUserCurrency();

  if (value === null || value === undefined) return "—";

  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: selectedCurrency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);

}

export function formatCompactCurrency(value) {

  const currency = getUserCurrency();

  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    notation: "compact",
    maximumFractionDigits: 1
  }).format(value);

}

export function parseCurrency(value) {

  if (!value) return 0;

  return Number(
    value.toString().replace(/[^0-9.-]+/g, "")
  );

}