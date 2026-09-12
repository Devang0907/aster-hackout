export type DecimalValue = number | string | null | undefined;

export function decimalNumber(value: DecimalValue): number {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function kgCo2eToTonnes(value: DecimalValue): number {
  return decimalNumber(value) / 1_000;
}

export function formatTonnes(value: DecimalValue, digits = 2): string {
  return kgCo2eToTonnes(value).toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function formatKgCo2eAsTonnes(value: DecimalValue, digits = 2): string {
  return `${formatTonnes(value, digits)} t CO₂e`;
}
