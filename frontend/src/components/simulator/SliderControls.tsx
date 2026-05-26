"use client";

import * as Slider from "@radix-ui/react-slider";

interface SliderControlsProps {
  expectedTraffic: number;
  averageSpend: number;
  baseRent: number;
  onTrafficChange: (value: number) => void;
  onSpendChange: (value: number) => void;
  onRentChange: (value: number) => void;
  maxTraffic: number;
  maxSpend: number;
  maxRent: number;
}

export function SliderControls({
  expectedTraffic,
  averageSpend,
  baseRent,
  onTrafficChange,
  onSpendChange,
  onRentChange,
  maxTraffic,
  maxSpend,
  maxRent,
}: SliderControlsProps) {
  return (
    <div className="h-full flex items-center gap-8 px-6">
      {/* Traffic Slider */}
      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-zinc-500 uppercase">
            Expected Traffic
          </span>
          <span className="text-xs font-mono text-white tabular-nums">
            {expectedTraffic}/day
          </span>
        </div>
        <Control value={expectedTraffic} max={maxTraffic} onChange={onTrafficChange} />
      </div>

      {/* Spend Slider */}
      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-zinc-500 uppercase">
            Target Spend
          </span>
          <span className="text-xs font-mono text-white tabular-nums">
            ${averageSpend}
          </span>
        </div>
        <Control value={averageSpend} max={maxSpend} onChange={onSpendChange} />
      </div>

      {/* Rent Slider */}
      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-zinc-500 uppercase">
            Occupancy Cost
          </span>
          <span className="text-xs font-mono text-white tabular-nums">
            ${baseRent.toLocaleString()}
          </span>
        </div>
        <Control value={baseRent} max={maxRent} step={100} onChange={onRentChange} />
      </div>
    </div>
  );
}

interface ControlProps {
  value: number;
  max: number;
  step?: number;
  onChange: (value: number) => void;
}

function Control({ value, max, step = 1, onChange }: ControlProps) {
  return (
    <Slider.Root
      min={0}
      max={max}
      step={step}
      value={[value]}
      onValueChange={([next]) => onChange(next)}
      className="relative flex h-4 w-full touch-none select-none items-center"
    >
      <Slider.Track className="relative h-1 grow rounded-full bg-zinc-800">
        <Slider.Range className="absolute h-full rounded-full bg-white" />
      </Slider.Track>
      <Slider.Thumb className="block h-3 w-3 rounded-full bg-white outline-none ring-white focus:ring-2" />
    </Slider.Root>
  );
}
