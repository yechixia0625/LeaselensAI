"use client";

import { AlertTriangle, Gauge, ShieldCheck } from "lucide-react";
import type { Summary } from "@/types/report";

interface ScoreBreakdownPanelProps {
  summary: Summary;
}

export function ScoreBreakdownPanel({ summary }: ScoreBreakdownPanelProps) {
  const breakdown = summary.scoreBreakdown;
  const fixedPercent = breakdown
    ? (breakdown.fixedScore / breakdown.maxFixedScore) * 100
    : summary.score;
  const displayedRiskFlags = breakdown ? sortRiskFlags(breakdown.riskFlags).slice(0, 6) : [];

  return (
    <section className="border-b border-zinc-800 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-[0.18em] text-zinc-500">
            <Gauge size={13} />
            Singapore lease score
          </div>
          <div className="mt-2 flex items-end gap-2">
            <span className="font-mono text-5xl font-bold text-white">
              {summary.score}
            </span>
            <span className="pb-2 font-mono text-xs text-zinc-500">/100</span>
          </div>
        </div>
        <div className="max-w-[8rem] text-right">
          <div className="inline-flex items-center gap-1 rounded border border-zinc-700 px-2 py-1 font-mono text-[10px] text-zinc-300">
            <ShieldCheck size={12} />
            {breakdown?.confidence ?? "LOW"}
          </div>
          <p className="mt-2 break-words font-mono text-[10px] uppercase text-zinc-500">
            {summary.verdict}
          </p>
        </div>
      </div>

      {breakdown && (
        <div className="mt-4 space-y-3">
          <ScoreBar
            label="Traceable model"
            value={breakdown.fixedScore}
            max={breakdown.maxFixedScore}
            percent={fixedPercent}
            tone="bg-lime-300"
          />

          <div className="space-y-2 pt-2">
            {breakdown.components.map((component) => (
              <div key={component.key} className="border border-zinc-800 bg-zinc-950 p-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate font-mono text-[11px] text-zinc-300">
                    {component.label}
                  </span>
                  <span className="shrink-0 font-mono text-[11px] text-zinc-500">
                    {component.score}/{component.maxScore}
                  </span>
                </div>
                <p className="mt-1 line-clamp-2 text-[11px] leading-4 text-zinc-500">
                  {component.rationale}
                </p>
                {component.assumptionsUsed && component.assumptionsUsed.length > 0 && (
                  <p className="mt-1 line-clamp-1 font-mono text-[10px] text-zinc-600">
                    {component.assumptionsUsed.length} assumptions
                  </p>
                )}
              </div>
            ))}
          </div>

          {breakdown.riskFlags.length > 0 && (
            <div className="space-y-2 border-t border-zinc-800 pt-3">
              <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500">
                <AlertTriangle size={12} />
                Risk flags
              </div>
              {displayedRiskFlags.map((flag) => (
                <div
                  key={`${flag.domain}-${flag.message}`}
                  className={`border px-2 py-1.5 text-[11px] leading-4 ${riskTone(flag.severity)}`}
                >
                  <div className="font-mono text-[10px] uppercase">
                    {flag.severity} / {flag.domain}
                  </div>
                  <p className="mt-0.5 text-zinc-300">{flag.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function sortRiskFlags<T extends { severity: string }>(riskFlags: T[]) {
  const priority: Record<string, number> = { critical: 0, warning: 1, info: 2 };
  return [...riskFlags].sort(
    (left, right) => (priority[left.severity] ?? 3) - (priority[right.severity] ?? 3),
  );
}

function riskTone(severity: string) {
  if (severity === "critical") {
    return "border-red-500/40 bg-red-500/5 text-red-300";
  }
  if (severity === "warning") {
    return "border-amber-500/40 bg-amber-500/5 text-amber-300";
  }
  return "border-zinc-800 bg-zinc-950 text-zinc-500";
}

interface ScoreBarProps {
  label: string;
  value: number;
  max: number;
  percent: number;
  tone: string;
}

function ScoreBar({ label, value, max, percent, tone }: ScoreBarProps) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.12em]">
        <span className="text-zinc-500">{label}</span>
        <span className="text-zinc-300">
          {value}/{max}
        </span>
      </div>
      <div className="h-1.5 bg-zinc-900">
        <div
          className={`h-full ${tone}`}
          style={{ width: `${Math.max(0, Math.min(100, percent))}%` }}
        />
      </div>
    </div>
  );
}
