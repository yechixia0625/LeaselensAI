/**
 * Calculate rent pressure as a percentage (0-100).
 * Higher values indicate rent is consuming more revenue.
 */
export function calculateRentPressure(
  baseRent: number,
  grossRevenue: number
): number {
  if (grossRevenue <= 0) return 100;
  return Math.min(100, (baseRent / grossRevenue) * 100);
}
