# 🚀 LeaseLens AI: Master Product & Technical Specification (All-in-One)

> **SYSTEM PROMPT FOR AI CODING AGENT:**
> You are a Staff-Level Full-Stack Architect and UI/UX Expert. You are tasked with building "LeaseLens AI", a Commercial Spatial Intelligence Platform. 
> This document contains the complete vision, tech stack, feature requirements, and data contracts. 
> **YOUR PRIME DIRECTIVE:** Read this ENTIRE document to understand the context. Do NOT generate all code at once. Acknowledge this document first, setup the initial project structure, and wait for the user to instruct you phase by phase.

---

## 1. PROJECT VISION & AESTHETICS
* **Product Definition:** An AI-native commercial lease decision engine. It acts as a "Venture Capital Partner + Architect" for entrepreneurs looking to rent commercial spaces.
* **User Experience:** "Zillow + Figma + McKinsey". The user uploads a photo/floorplan, inputs basic metrics (rent, size, business type), and gets a real-time spatial and financial analysis.
* **Aesthetic Style:** **Architect + VC Minimalist**. 
    * Pure monochrome (Black/White/Zinc/Slate).
    * High-contrast, borderless UI.
    * Backgrounds should feature subtle dotted blueprint grids.
    * Typography: Sans-serif for UI, Monospace for AI terminal outputs.
    * No traditional "SaaS" forms. Interactions must feel like a futuristic spatial OS.

---

## 2. TECH STACK & ARCHITECTURE
We are using a decoupled monorepo architecture.
* **Frontend (Next.js 14 App Router, TypeScript):**
    * *UI/Styling:* Tailwind CSS, Shadcn UI, Lucide React.
    * *Animations:* Framer Motion (crucial for smooth transitions and the "Verdict Stamp").
    * *Visualization:* Recharts (for gauges/charts), Leaflet.js (for maps with Dark Matter no-label tiles), and raw HTML5 `<svg>` (for rendering spatial blueprints, no Three.js).
    * *State:* React hooks (`useMemo`, `useState`) for zero-latency client-side math calculations.
* **Backend (Python 3.11+, FastAPI):**
    * *Core:* FastAPI (async) for handling high-concurrency LLM streaming.
    * *AI Orchestration:* `asyncio.gather` to run multiple LLM prompts concurrently.
    * *Streaming:* Server-Sent Events (SSE) via `StreamingResponse`.
    * *Data Validation:* Pydantic (Strict typing for JSON outputs).
* **Infrastructure (Docker Compose):**
    * Containers for: Next.js (web), FastAPI (api), PostgreSQL w/ pgvector (db), Redis (cache), Nginx (proxy).

---

## 3. CORE FEATURES & PRD (Product Requirements Document)

### Module 1: I/O & Onboarding
* **Minimalist Intake Form:** A full-screen drag-and-drop zone for space photos/floorplans. Include 3 simple inputs: Target Business (e.g., Cafe), Expected Rent, and Square Meters.
* **Hacker-style Loading:** Upon clicking "Analyze", transition to the main workspace. Do not use spinners. Use rapid, blinking terminal text (e.g., `[Initializing Spatial Matrix...]`).

### Module 2: Left Pane - Spatial & Map Engine (5 Columns)
* **SVG Blueprint Renderer:** Instead of heavy 3D, parse the backend's JSON to draw a dynamic 2D SVG blueprint. Use strokes for walls, arcs for doors.
* **Heatmap Overlay:** Apply absolute positioned `<div>` or `<circle>` elements with CSS `blur-2xl` and opacity over the SVG to represent "High Profit" and "Dead Zones".
* **Map Toggle:** A button to flip the blueprint into a `React Leaflet` map (Dark mode, no labels). Render competitors as simple high-contrast dots.

### Module 3: Middle Pane - Multi-Agent Terminal (4 Columns)
* **Concurrent Log Streaming:** Split into 4 terminal boxes: `[Spatial]`, `[Finance]`, `[Competition]`, `[Strategy]`.
* **Behavior:** Listen to the backend SSE stream. Text must appear line-by-line simultaneously across all 4 boxes, simulating 4 AI brains thinking concurrently.
* **Verdict Stamp Animation:** Once the stream ends, use Framer Motion to drop a massive text stamp in the center (e.g., `APPROVED WITH CONDITIONS`).

### Module 4: Right & Bottom Pane - What-If Simulator (3 Columns + Bottom Fixed)
* **Zero-Latency Math Engine:** Use pure React `useMemo`. Formula: `Net Profit = (Traffic * Spend * Conversion) - Rent - Fixed Costs`.
* **Three-way Slider Control (Bottom):** Render Shadcn Sliders for `Expected Traffic`, `Target Spend`, and `Negotiated Rent`. Dragging these must update the math engine instantly *without* calling the backend API.
* **Dynamic Gauge & Payback Metric (Right):** Render a Recharts Gauge for "Rent Pressure". Render a massive number for "Payback Months". If Net Profit < 0, the text turns red/blinks `CRITICAL`.

### Module 5: Python API & Streaming Engine
* **Endpoint:** `POST /api/analyze-space` (accepts multipart/form-data).
* **Logic:** Trigger 4 async AI tasks. Yield logs as SSE. 
* **Final Output:** The very last chunk of the SSE stream MUST be a complete JSON object matching the `LeaseLensReport` schema below.

---

## 4. CORE DATA CONTRACT (The Source of Truth)
The Python backend must ultimately generate and stream this exact JSON structure to the Next.js frontend. The frontend relies completely on this to render the blueprint and initialize the math engine.

```json
{
  "summary": {
    "score": 82,
    "verdict": "APPROVED WITH CONDITIONS",
    "paybackMonths": 9.2
  },
  "spatialBlueprint": {
    "aspectRatio": 1.5,
    "elements": [
      { "type": "door", "x": 0, "y": 40, "w": 5, "h": 20, "label": "Main Entrance" },
      { "type": "window", "x": 0, "y": 0, "w": 5, "h": 30, "label": "Street Display" }
    ],
    "heatZones": [
      { "x": 20, "y": 20, "radius": 15, "intensity": 0.9, "type": "high_profit" },
      { "x": 80, "y": 80, "radius": 20, "intensity": 0.2, "type": "dead_zone" }
    ]
  },
  "financialModel": {
    "baseRent": 5200,
    "expectedTraffic": 120,
    "conversionRate": 0.08,
    "averageSpend": 35,
    "grossMargin": 0.65,
    "fixedCostNonRent": 2000,
    "initialDecorationCost": 45000
  },
  "mapData": {
    "center": [31.2304, 121.4737],
    "competitors": [
      { "name": "Starbucks", "lat": 31.2310, "lng": 121.4740, "type": "coffee", "proximityLevel": "HIGH" }
    ]
  }
}
