"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LoginPanel } from "@/components/auth/LoginPanel";
import { DropZone } from "@/components/intake/DropZone";
import {
  DEFAULT_INTAKE_FORM_VALUES,
  IntakeForm,
  type IntakeFormValues,
} from "@/components/intake/IntakeForm";
import { AnalyzeButton } from "@/components/intake/AnalyzeButton";
import { LocationSelector } from "@/components/intake/LocationSelector";
import { AuthService } from "@/services/authService";
import { storePendingAnalysis } from "@/services/intakeTransfer";
import type { AnalysisIntake, SiteLocation } from "@/services/intakeTransfer";

export default function IntakePage() {
  const router = useRouter();
  const [authChecked, setAuthChecked] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [formValues, setFormValues] = useState<IntakeFormValues>(
    DEFAULT_INTAKE_FORM_VALUES
  );
  const [location, setLocation] = useState<SiteLocation | null>(null);

  const supportedFile =
    file !== null &&
    ["image/png", "image/jpeg", "image/webp"].includes(file.type) &&
    file.size <= 10 * 1024 * 1024;
  const canAnalyze =
    supportedFile &&
    formValues.businessType.trim() !== "" &&
    Number(formValues.expectedRent) > 0 &&
    Number(formValues.squareMeters) > 0 &&
    Number(formValues.leaseTermMonths) > 0 &&
    Number(formValues.serviceChargeMonthly) >= 0 &&
    Number(formValues.fitoutBudget) >= 0 &&
    location !== null;

  useEffect(() => {
    let active = true;
    AuthService.session()
      .then((session) => {
        if (!active) return;
        setAuthenticated(session.authenticated);
      })
      .catch(() => {
        if (!active) return;
        setAuthenticated(false);
      })
      .finally(() => {
        if (active) setAuthChecked(true);
      });

    return () => {
      active = false;
    };
  }, []);

  const handleAnalyze = () => {
    if (!canAnalyze) return;
    const intake = buildAnalysisIntake(formValues, location!);

    storePendingAnalysis({
      file: file!,
      intake,
    });

    router.push("/workspace");
  };

  if (!authChecked) {
    return (
      <main className="min-h-screen blueprint-grid flex items-center justify-center p-8">
        <div className="font-mono text-xs tracking-[0.18em] text-zinc-500">CHECKING SESSION...</div>
      </main>
    );
  }

  if (!authenticated) {
    return (
      <main className="min-h-screen blueprint-grid flex items-center justify-center p-8">
        <LoginPanel onSuccess={() => setAuthenticated(true)} />
      </main>
    );
  }

  return (
    <main className="min-h-screen blueprint-grid flex items-center justify-center p-8">
      <div className="w-full max-w-2xl space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">
            Lease<span className="text-zinc-500">Lens</span>
          </h1>
          <p className="text-zinc-500 font-mono text-sm">
            Singapore shop-location intelligence for small businesses
          </p>
        </div>

        {/* Drop Zone */}
        <DropZone file={file} onFileChange={setFile} />
        {file && !supportedFile && (
          <p className="text-xs font-mono text-red-500">
            Upload a PNG, JPG, or WEBP image no larger than 10MB.
          </p>
        )}

        {/* Form */}
        <IntakeForm
          values={formValues}
          onChange={(key, value) =>
            setFormValues((current) => ({ ...current, [key]: value }))
          }
        />

        <LocationSelector value={location} onChange={setLocation} />

        {/* Analyze Button */}
        <AnalyzeButton disabled={!canAnalyze} onClick={handleAnalyze} />
      </div>
    </main>
  );
}

function buildAnalysisIntake(
  values: IntakeFormValues,
  location: SiteLocation
): AnalysisIntake {
  return {
    businessType: values.businessType,
    expectedRent: toRequiredNumber(values.expectedRent),
    squareMeters: toRequiredNumber(values.squareMeters),
    leaseTermMonths: toRequiredNumber(values.leaseTermMonths),
    serviceChargeMonthly: toRequiredNumber(values.serviceChargeMonthly),
    fitoutBudget: toRequiredNumber(values.fitoutBudget),
    cookingIntensity: values.cookingIntensity,
    floorPosition: values.floorPosition,
    layoutShape: values.layoutShape,
    hasWaterSupply: values.hasWaterSupply,
    hasFloorTrap: values.hasFloorTrap,
    hasGreaseTrap: values.hasGreaseTrap,
    electricalReadiness: values.electricalReadiness,
    hasGas: values.hasGas,
    hasExhaust: values.hasExhaust,
    wastewaterReadiness: values.wastewaterReadiness,
    approvedUseStatus: values.approvedUseStatus,
    rentFreeMonths: toOptionalNumber(values.rentFreeMonths),
    depositMonths: toOptionalNumber(values.depositMonths),
    otherMonthlyCosts: toOptionalNumber(values.otherMonthlyCosts),
    utilitiesMonthlyEstimate: toOptionalNumber(values.utilitiesMonthlyEstimate),
    staffingMonthly: toOptionalNumber(values.staffingMonthly),
    marketingMonthly: toOptionalNumber(values.marketingMonthly),
    insuranceMonthly: toOptionalNumber(values.insuranceMonthly),
    licenseFees: toOptionalNumber(values.licenseFees),
    reinstatementCost: toOptionalNumber(values.reinstatementCost),
    expectedDailyCustomers: toOptionalNumber(values.expectedDailyCustomers),
    averageSpend: toOptionalNumber(values.averageSpend),
    grossMargin: toOptionalNumber(values.grossMargin),
    frontageWidthM: toOptionalNumber(values.frontageWidthM),
    ceilingHeightM: toOptionalNumber(values.ceilingHeightM),
    usableAreaRatio: toOptionalNumber(values.usableAreaRatio),
    storageAreaSqm: toOptionalNumber(values.storageAreaSqm),
    seatingCapacity: toOptionalNumber(values.seatingCapacity),
    loadingAccess: values.loadingAccess,
    toiletAccess: values.toiletAccess,
    signageVisibility: values.signageVisibility,
    exhaustRouteAvailable: values.exhaustRouteAvailable,
    location,
  };
}

function toRequiredNumber(value: string): number {
  return Number(value);
}

function toOptionalNumber(value: string): number | undefined {
  if (value.trim() === "") return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}
