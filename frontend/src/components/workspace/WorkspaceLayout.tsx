"use client";

import { useState } from "react";
import type { LeaseLensReport } from "@/types/report";
import { SVGBlueprint } from "@/components/spatial/SVGBlueprint";
import { MapToggle } from "@/components/spatial/MapToggle";
import { TerminalGrid } from "@/components/workspace/TerminalGrid";
import { WhatIfPanel } from "@/components/simulator/WhatIfPanel";
import { SliderControls } from "@/components/simulator/SliderControls";
import { useWhatIf } from "@/hooks/useWhatIf";
import type { AnalysisIntake } from "@/services/intakeTransfer";
import type { AgentLogEvent } from "@/types/streaming";
import { ScoreBreakdownPanel } from "./ScoreBreakdownPanel";
import { LocationRecommendations } from "./LocationRecommendations";

interface WorkspaceLayoutProps {
  intake: AnalysisIntake;
  report: LeaseLensReport | null;
  agentLogs: Record<string, AgentLogEvent[]>;
  status: string;
  error: string | null;
}

export function WorkspaceLayout({
  intake,
  report,
  agentLogs,
  status,
  error,
}: WorkspaceLayoutProps) {
  const [showMap, setShowMap] = useState(false);
  const occupancyCost =
    report?.financialModel.totalMonthlyOccupancyCost ??
    intake.expectedRent + intake.serviceChargeMonthly;
  const nonOccupancyCost =
    report?.financialModel.monthlyOperatingCost && report.financialModel.totalMonthlyOccupancyCost
      ? Math.max(
          report.financialModel.monthlyOperatingCost -
            report.financialModel.totalMonthlyOccupancyCost,
          0
        )
      : report?.financialModel.fixedCostNonRent ?? 2000;

  const whatIf = useWhatIf(
    {
      expectedTraffic: report?.financialModel.expectedTraffic ?? 120,
      averageSpend: report?.financialModel.averageSpend ?? 35,
      conversionRate: report?.financialModel.conversionRate ?? 0.08,
      grossMargin: report?.financialModel.grossMargin ?? 0.65,
      baseRent: occupancyCost,
      fixedCostNonRent: nonOccupancyCost,
      initialDecorationCost:
        report?.financialModel.setupCapitalRequired ??
        report?.financialModel.initialDecorationCost,
    },
    {
      expectedTraffic: report?.financialModel.expectedTraffic,
      averageSpend: report?.financialModel.averageSpend,
      baseRent: occupancyCost,
    }
  );

  return (
    <div className="h-screen flex flex-col bg-black">
      {/* Top bar */}
      <div className="h-10 border-b border-zinc-800 flex items-center px-4 shrink-0">
        <span className="font-mono text-xs text-zinc-500">
          LeaseLens<span className="text-white">AI</span>
        </span>
        <span className="mx-2 text-zinc-700">/</span>
        <span className="font-mono text-xs text-zinc-400">
          {intake.businessType} - {intake.squareMeters}sqm
        </span>
        <div className="ml-auto flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span className="font-mono text-xs text-zinc-500">LIVE</span>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: Spatial (5 cols) */}
        <div className="w-5/12 border-r border-zinc-800 relative overflow-hidden">
          {report && showMap ? (
            <MapToggle
              mapData={report.mapData}
            />
          ) : (
            <>
              {report?.spatialBlueprint ? (
                <SVGBlueprint blueprint={report.spatialBlueprint} />
              ) : (
                <div className="h-full flex items-center justify-center font-mono text-xs text-zinc-500">
                  [ANALYZING SPATIAL MATRIX...]
                </div>
              )}
            </>
          )}
          <button
            onClick={() => setShowMap(!showMap)}
            className="absolute top-4 right-4 px-3 py-1.5 bg-zinc-900/95 border border-zinc-700 rounded text-xs font-mono hover:bg-zinc-800 transition-colors z-[700]"
          >
            {showMap ? "Decision Plan" : "Live Market"}
          </button>
        </div>

        {/* Middle Pane: Terminals (4 cols) */}
        <div className="w-4/12 border-r border-zinc-800 flex flex-col">
          <TerminalGrid
            agentLogs={agentLogs}
            verdict={report?.summary.verdict}
            isComplete={status === "complete"}
          />
        </div>

        {/* Right Pane: Decision Panel (3 cols) */}
        <div className="w-3/12 flex flex-col overflow-y-auto">
          {report ? (
            <>
              <ScoreBreakdownPanel summary={report.summary} />
              <WhatIfPanel
                result={whatIf.result}
                paybackMonths={whatIf.paybackMonths}
                rentPressure={whatIf.rentPressure}
                initialCost={
                  report.financialModel.setupCapitalRequired ||
                  report.financialModel.initialDecorationCost
                }
              />
              <LocationRecommendations locations={report.recommendedLocations} />
            </>
          ) : (
            <div className="p-4 font-mono text-xs text-zinc-500">
              [{error ? `ERROR: ${error}` : "AWAITING FINANCIAL REPORT..."}]
            </div>
          )}
        </div>
      </div>

      {/* Bottom: Slider Controls */}
      <div className="h-24 border-t border-zinc-800 shrink-0">
        {report && <SliderControls
          expectedTraffic={whatIf.sliders.expectedTraffic}
          averageSpend={whatIf.sliders.averageSpend}
          baseRent={whatIf.sliders.baseRent}
          onTrafficChange={(v) => whatIf.setSlider("expectedTraffic", v)}
          onSpendChange={(v) => whatIf.setSlider("averageSpend", v)}
          onRentChange={(v) => whatIf.setSlider("baseRent", v)}
          maxTraffic={500}
          maxSpend={100}
          maxRent={30000}
        />}
      </div>
    </div>
  );
}
