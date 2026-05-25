"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LoginPanel } from "@/components/auth/LoginPanel";
import { DropZone } from "@/components/intake/DropZone";
import { IntakeForm } from "@/components/intake/IntakeForm";
import { AnalyzeButton } from "@/components/intake/AnalyzeButton";
import { LocationSelector } from "@/components/intake/LocationSelector";
import { AuthService } from "@/services/authService";
import { storePendingAnalysis } from "@/services/intakeTransfer";
import type { SiteLocation } from "@/services/intakeTransfer";

export default function IntakePage() {
  const router = useRouter();
  const [authChecked, setAuthChecked] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [businessType, setBusinessType] = useState("");
  const [expectedRent, setExpectedRent] = useState("");
  const [squareMeters, setSquareMeters] = useState("");
  const [location, setLocation] = useState<SiteLocation | null>(null);

  const supportedFile =
    file !== null &&
    ["image/png", "image/jpeg", "image/webp"].includes(file.type) &&
    file.size <= 10 * 1024 * 1024;
  const canAnalyze =
    supportedFile &&
    businessType.trim() !== "" &&
    Number(expectedRent) > 0 &&
    Number(squareMeters) > 0 &&
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

    storePendingAnalysis({
      file: file!,
      intake: {
        businessType,
        expectedRent: parseFloat(expectedRent),
        squareMeters: parseFloat(squareMeters),
        location: location!,
      },
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
            Commercial Spatial Intelligence Platform
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
          businessType={businessType}
          expectedRent={expectedRent}
          squareMeters={squareMeters}
          onBusinessTypeChange={setBusinessType}
          onExpectedRentChange={setExpectedRent}
          onSquareMetersChange={setSquareMeters}
        />

        <LocationSelector value={location} onChange={setLocation} />

        {/* Analyze Button */}
        <AnalyzeButton disabled={!canAnalyze} onClick={handleAnalyze} />
      </div>
    </main>
  );
}
