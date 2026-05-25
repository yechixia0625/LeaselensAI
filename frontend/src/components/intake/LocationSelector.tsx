"use client";

import { useEffect, useState } from "react";
import { Crosshair, MapPin, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { isUnauthorizedError } from "@/services/authService";
import { LocationService, type LocationPrediction } from "@/services/locationService";
import type { SiteLocation } from "@/services/intakeTransfer";

interface LocationSelectorProps {
  value: SiteLocation | null;
  onChange: (value: SiteLocation | null) => void;
}

function createSessionToken() {
  if (typeof globalThis.crypto?.randomUUID === "function") {
    return globalThis.crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
}

export function LocationSelector({ value, onChange }: LocationSelectorProps) {
  const [mode, setMode] = useState<"current" | "address">("current");
  const [query, setQuery] = useState("");
  const [predictions, setPredictions] = useState<LocationPrediction[]>([]);
  const [sessionToken, setSessionToken] = useState(createSessionToken);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (mode !== "address" || query.trim().length < 2 || value?.mode === "address") {
      setPredictions([]);
      return;
    }
    const timeout = window.setTimeout(async () => {
      setPending(true);
      setError(null);
      try {
        setPredictions(await LocationService.autocomplete(query.trim(), sessionToken));
      } catch (err) {
        if (isUnauthorizedError(err)) {
          setError("Session expired. Please sign in again.");
          window.location.href = "/";
          return;
        }
        setError("Address suggestions are unavailable.");
      } finally {
        setPending(false);
      }
    }, 350);
    return () => window.clearTimeout(timeout);
  }, [mode, query, sessionToken, value?.mode]);

  function switchMode(nextMode: "current" | "address") {
    setMode(nextMode);
    onChange(null);
    setError(null);
    setPredictions([]);
    setQuery("");
    setSessionToken(createSessionToken());
  }

  function locateCurrentSite() {
    setPending(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        onChange({ mode: "current", latitude: coords.latitude, longitude: coords.longitude });
        setPending(false);
      },
      () => {
        setError("Location permission denied. Search an address instead.");
        setPending(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  async function choosePrediction(prediction: LocationPrediction) {
    setPending(true);
    setError(null);
    try {
      const resolved = await LocationService.resolve(prediction.placeId, sessionToken);
      onChange(resolved);
      setQuery(resolved.siteLabel ?? prediction.text);
      setPredictions([]);
    } catch (err) {
      if (isUnauthorizedError(err)) {
        setError("Session expired. Please sign in again.");
        window.location.href = "/";
        return;
      }
      setError("Could not resolve this address.");
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="border border-zinc-800 bg-zinc-950/70 rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs tracking-[0.18em] text-zinc-500">SITE LOCATION</span>
        {value && <span className="font-mono text-[10px] text-lime-300">VERIFIED</span>}
      </div>
      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={() => switchMode("current")}
          className={cn(
            "flex items-center justify-center gap-2 px-3 py-2 border rounded font-mono text-xs",
            mode === "current" ? "border-lime-300 text-lime-200 bg-lime-300/5" : "border-zinc-800 text-zinc-500"
          )}
        >
          <Crosshair className="w-3.5 h-3.5" /> At site now
        </button>
        <button
          type="button"
          onClick={() => switchMode("address")}
          className={cn(
            "flex items-center justify-center gap-2 px-3 py-2 border rounded font-mono text-xs",
            mode === "address" ? "border-lime-300 text-lime-200 bg-lime-300/5" : "border-zinc-800 text-zinc-500"
          )}
        >
          <Search className="w-3.5 h-3.5" /> Search address
        </button>
      </div>
      {mode === "current" ? (
        <div className="space-y-3">
          <p className="text-xs leading-relaxed text-zinc-500">
            Use this only while physically at the retail site being evaluated.
          </p>
          <button
            type="button"
            disabled={pending}
            onClick={locateCurrentSite}
            className="w-full border border-zinc-700 py-2 font-mono text-xs hover:border-lime-300 disabled:opacity-50"
          >
            {pending ? "LOCATING..." : value?.mode === "current" ? "LOCATION CONFIRMED" : "AUTHORIZE LOCATION"}
          </button>
        </div>
      ) : (
        <div className="relative space-y-2">
          <input
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              onChange(null);
            }}
            placeholder="Search the retail site address"
            className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-sm font-mono focus:outline-none focus:border-zinc-600"
          />
          {predictions.length > 0 && (
            <div className="absolute top-full z-20 w-full border border-zinc-700 bg-zinc-950 shadow-xl">
              {predictions.map((prediction) => (
                <button
                  type="button"
                  key={prediction.placeId}
                  onClick={() => choosePrediction(prediction)}
                  className="flex w-full items-start gap-2 border-b border-zinc-800 p-3 text-left text-xs text-zinc-300 hover:bg-zinc-900"
                >
                  <MapPin className="mt-0.5 h-3.5 w-3.5 shrink-0 text-lime-300" />
                  {prediction.text}
                </button>
              ))}
            </div>
          )}
          <p className="text-[11px] text-zinc-500">
            Select a matched address to verify coordinates before analysis.
          </p>
        </div>
      )}
      {error && <p className="font-mono text-xs text-red-400">{error}</p>}
    </section>
  );
}
