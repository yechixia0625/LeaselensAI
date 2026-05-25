"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { WorkspaceLayout } from "@/components/workspace/WorkspaceLayout";
import { HackerLoading } from "@/components/workspace/HackerLoading";
import { useSSEStream } from "@/hooks/useSSEStream";
import { AnalysisService } from "@/services/AnalysisService";
import { AuthService } from "@/services/authService";
import {
  getPendingAnalysis,
  type AnalysisIntake,
} from "@/services/intakeTransfer";

export default function WorkspacePage() {
  const router = useRouter();
  const [authChecked, setAuthChecked] = useState(false);
  const [intake, setIntake] = useState<AnalysisIntake | null>(null);
  const { status, agentLogs, finalReport, error, connect } = useSSEStream();

  useEffect(() => {
    let active = true;
    AuthService.session()
      .then((session) => {
        if (!active) return;
        if (!session.authenticated) {
          router.replace("/");
          return;
        }
        const pending = getPendingAnalysis();
        if (!pending) {
          router.replace("/");
          return;
        }
        setIntake(pending.intake);
        connect(AnalysisService.createFormData(pending.file, pending.intake));
        setAuthChecked(true);
      })
      .catch(() => {
        if (active) {
          router.replace("/");
        }
      });

    return () => {
      active = false;
    };
  }, [connect, router]);

  useEffect(() => {
    if (error === "unauthorized") {
      router.replace("/");
    }
  }, [error, router]);

  if (!authChecked || !intake) {
    return <HackerLoading />;
  }

  return (
    <WorkspaceLayout
      intake={intake}
      report={finalReport}
      agentLogs={agentLogs}
      status={status}
      error={error}
    />
  );
}
