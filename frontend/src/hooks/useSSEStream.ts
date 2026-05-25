"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { ANALYSIS_API_PATH } from "@/services/AnalysisService";
import { UnauthorizedError } from "@/services/authService";
import { classifySSEPayload } from "@/lib/sse";
import type { LeaseLensReport } from "@/types/report";
import type { AgentLogEvent } from "@/types/streaming";

type StreamStatus = "idle" | "connecting" | "streaming" | "complete" | "error";

interface UseSSEStreamReturn {
  status: StreamStatus;
  agentLogs: Record<string, AgentLogEvent[]>;
  finalReport: LeaseLensReport | null;
  error: string | null;
  connect: (formData: FormData) => void;
  disconnect: () => void;
}

export function useSSEStream(): UseSSEStreamReturn {
  const abortRef = useRef<AbortController | null>(null);
  const [status, setStatus] = useState<StreamStatus>("idle");
  const [agentLogs, setAgentLogs] = useState<Record<string, AgentLogEvent[]>>({
    spatial: [],
    finance: [],
    competition: [],
    strategy: [],
  });
  const [finalReport, setFinalReport] = useState<LeaseLensReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const disconnect = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  const connect = useCallback(
    async (formData: FormData) => {
      disconnect();
      setStatus("connecting");
      setError(null);
      setAgentLogs({
        spatial: [],
        finance: [],
        competition: [],
        strategy: [],
      });
      setFinalReport(null);

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const response = await fetch(ANALYSIS_API_PATH, {
          method: "POST",
          body: formData,
          credentials: "include",
          signal: controller.signal,
        });

        if (response.status === 401) {
          throw new UnauthorizedError();
        }
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        setStatus("streaming");

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let receivedReport = false;
        let receivedError = false;

        if (!reader) throw new Error("No response body");

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Parse SSE events from buffer
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const payload = classifySSEPayload(JSON.parse(line.slice(6)));

                if (payload.kind === "agent_log") {
                  setAgentLogs((prev) => ({
                    ...prev,
                    [payload.event.agent]: [
                      ...(prev[payload.event.agent] ?? []),
                      payload.event,
                    ],
                  }));
                } else if (payload.kind === "report") {
                  receivedReport = true;
                  setFinalReport(payload.report);
                  setStatus("complete");
                } else if (payload.kind === "error") {
                  receivedError = true;
                  setError(payload.event.message);
                  setStatus("error");
                }
              } catch {
                // Skip malformed JSON
              }
            }
          }
        }

        if (!receivedReport && !receivedError) {
          throw new Error("Analysis stream ended without a final report.");
        }
      } catch (err) {
        if ((err as Error).name === "AbortError") return;
        setError((err as Error).message);
        setStatus("error");
      }
    },
    [disconnect]
  );

  useEffect(() => () => disconnect(), [disconnect]);

  return { status, agentLogs, finalReport, error, connect, disconnect };
}
