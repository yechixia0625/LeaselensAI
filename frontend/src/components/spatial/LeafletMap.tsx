"use client";

import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import type { MapData, Competitor } from "@/types/map";
import { DARK_TILES_ATTRIBUTION, DARK_TILES_URL, DEFAULT_MAP_ZOOM } from "@/lib/map-tiles";

interface LeafletMapProps {
  mapData: MapData;
}

function markerColor(proximityLevel: Competitor["proximityLevel"]): string {
  if (proximityLevel === "HIGH") return "#e16855";
  if (proximityLevel === "MEDIUM") return "#e4bb63";
  return "#79a984";
}

export default function LeafletMap({ mapData }: LeafletMapProps) {
  return (
    <div className="relative h-full w-full">
      <div className="absolute left-4 top-4 z-[500] space-y-1 bg-black/90 px-3 py-2 font-mono">
        <p className="text-[10px] tracking-[0.2em] text-lime-300">LIVE MARKET / GOOGLE PLACES</p>
        <p className="text-[10px] text-zinc-400">
          {mapData.locationMode === "current" ? "CURRENT LOCATION" : "SELECTED ADDRESS"} / {mapData.searchRadiusMeters} M
        </p>
      </div>
      <MapContainer center={mapData.center} zoom={DEFAULT_MAP_ZOOM} className="h-full w-full">
        <TileLayer url={DARK_TILES_URL} attribution={DARK_TILES_ATTRIBUTION} />
        <CircleMarker
          center={mapData.center}
          radius={10}
          pathOptions={{ color: "#bed269", weight: 3, fillColor: "#bed269", fillOpacity: 0.65 }}
        >
          <Popup>
            <strong>Target Site</strong>
            <br />
            {mapData.siteLabel ?? "Current location"}
          </Popup>
        </CircleMarker>
        {mapData.status === "available" &&
          mapData.competitors.map((competitor) => (
            <CircleMarker
              key={`${competitor.name}-${competitor.lat}-${competitor.lng}`}
              center={[competitor.lat, competitor.lng]}
              radius={6}
              pathOptions={{
                color: "#ffffff",
                weight: 2,
                fillColor: markerColor(competitor.proximityLevel),
                fillOpacity: 1,
              }}
            >
              <Popup>
                <span className="font-mono text-xs">
                  <strong>{competitor.name}</strong>
                  <br />
                  {competitor.type} / {competitor.distanceMeters} M
                  <br />
                  Proximity: {competitor.proximityLevel}
                </span>
              </Popup>
            </CircleMarker>
          ))}
      </MapContainer>
      <div className="absolute bottom-6 left-4 right-4 z-[500] border border-zinc-700 bg-black/90 p-3 font-mono text-[10px]">
        {mapData.status === "unavailable" ? (
          <span className="text-amber-300">{mapData.message ?? "Live nearby-place data is unavailable."}</span>
        ) : (
          <span className="text-zinc-300">
            {mapData.competitors.length} VERIFIED NEARBY LOCATIONS / PROXIMITY LEVEL DERIVED FROM DISTANCE
          </span>
        )}
      </div>
    </div>
  );
}
