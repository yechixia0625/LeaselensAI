"use client";

import { useMemo, useState, useCallback } from "react";
import {
  calculateProfit,
  calculatePaybackMonths,
  calculateRentPressure,
} from "@/math";
import type { ProfitInput, ProfitResult } from "@/math/profit";

interface WhatIfState {
  expectedTraffic: number;
  averageSpend: number;
  baseRent: number;
}

interface UseWhatIfReturn {
  sliders: WhatIfState;
  setSlider: <K extends keyof WhatIfState>(
    key: K,
    value: WhatIfState[K]
  ) => void;
  result: ProfitResult;
  paybackMonths: number;
  rentPressure: number;
}

export function useWhatIf(
  baseInput: ProfitInput & { initialDecorationCost?: number },
  initialOverrides?: Partial<WhatIfState>
): UseWhatIfReturn {
  const baseline = useMemo<WhatIfState>(
    () => ({
      expectedTraffic:
        initialOverrides?.expectedTraffic ?? baseInput.expectedTraffic,
      averageSpend: initialOverrides?.averageSpend ?? baseInput.averageSpend,
      baseRent: initialOverrides?.baseRent ?? baseInput.baseRent,
    }),
    [
      baseInput.averageSpend,
      baseInput.baseRent,
      baseInput.expectedTraffic,
      initialOverrides?.averageSpend,
      initialOverrides?.baseRent,
      initialOverrides?.expectedTraffic,
    ]
  );
  const baselineKey = `${baseline.expectedTraffic}:${baseline.averageSpend}:${baseline.baseRent}`;
  const [sliderState, setSliderState] = useState<{ key: string; sliders: WhatIfState }>(
    {
      key: baselineKey,
      sliders: baseline,
    }
  );
  const sliders = sliderState.key === baselineKey ? sliderState.sliders : baseline;

  const setSlider = useCallback(
    <K extends keyof WhatIfState>(key: K, value: WhatIfState[K]) => {
      setSliderState((prev) => {
        const current = prev.key === baselineKey ? prev.sliders : baseline;
        return {
          key: baselineKey,
          sliders: { ...current, [key]: value },
        };
      });
    },
    [baseline, baselineKey]
  );

  const profitInput: ProfitInput = useMemo(
    () => ({
      ...baseInput,
      ...sliders,
    }),
    [baseInput, sliders]
  );

  const result = useMemo(() => calculateProfit(profitInput), [profitInput]);

  const paybackMonths = useMemo(
    () =>
      calculatePaybackMonths(
        baseInput.initialDecorationCost ?? 45000,
        result.netProfit
      ),
    [result.netProfit, baseInput.initialDecorationCost]
  );

  const rentPressure = useMemo(
    () => calculateRentPressure(profitInput.baseRent, result.grossRevenue),
    [profitInput.baseRent, result.grossRevenue]
  );

  return { sliders, setSlider, result, paybackMonths, rentPressure };
}
