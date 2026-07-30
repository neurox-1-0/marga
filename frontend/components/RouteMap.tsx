'use client';

import React, { useState, useMemo } from 'react';
import DeckGL from '@deck.gl/react';
import { ArcLayer, ScatterplotLayer, TextLayer, BitmapLayer, PathLayer } from '@deck.gl/layers';
import { TileLayer } from '@deck.gl/geo-layers';
import type { PickingInfo } from '@deck.gl/core';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface RouteMapProps {
  activeStep?: number;
  onSelectRoute?: (routeId: string) => void;
}

interface Port {
  id: string;
  name: string;
  code: string;
  coordinates: [number, number]; // [lng, lat]
  type: 'origin' | 'destination' | 'disruption' | 'hub';
  status: 'normal' | 'disrupted' | 'rerouted';
  details: string;
}

interface ShippingArc {
  id: string;
  from: { coordinates: [number, number] };
  to: { coordinates: [number, number] };
  path?: [number, number][];
  type: 'sea' | 'air' | 'secondary';
  label: string;
}

// ---------------------------------------------------------------------------
// Static data — real lat/lng coordinates
// ---------------------------------------------------------------------------

const PORTS: Port[] = [
  {
    id: 'port-shanghai',
    name: 'Port of Shanghai',
    code: 'CNSHA',
    coordinates: [121.47, 31.23],
    type: 'origin',
    status: 'disrupted',
    details: 'Origin Port · 8 Impacted Shipments ($1.25M Inventory)',
  },
  {
    id: 'disruption-shanghai',
    name: 'East China Sea Disruption',
    code: 'TYPHOON-01',
    coordinates: [125.0, 30.0],
    type: 'disruption',
    status: 'disrupted', // overridden reactively
    details: 'Typhoon Alert · +7 Days Maritime Delay · Active Typhoon Warning',
  },
  {
    id: 'port-lax',
    name: 'Port of Los Angeles',
    code: 'USLAX',
    coordinates: [241.74, 33.73], // 360 - 118.26 to place it east of Asia
    type: 'destination',
    status: 'normal',
    details: 'Destination Hub · Destination for PO-101 & PO-102',
  },
  {
    id: 'port-suez',
    name: 'Suez Canal Hub',
    code: 'EGSUE',
    coordinates: [32.33, 30.57],
    type: 'hub',
    status: 'normal',
    details: 'Middle East Transit Channel · Flowing Normal',
  },
  {
    id: 'port-rotterdam',
    name: 'Port of Rotterdam',
    code: 'NLRTM',
    coordinates: [4.49, 51.9],
    type: 'hub',
    status: 'normal',
    details: 'European Gateway · Flowing Normal',
  },
];

const ARCS: ShippingArc[] = [
  {
    id: 'sea-route',
    from: { coordinates: [121.47, 31.23] },
    to: { coordinates: [241.74, 33.73] }, // LA is -118.26, mapped to 360-118.26 to avoid wrap
    path: [
      [121.47, 31.23], // Shanghai
      [123.5, 29.5],   // East China Sea
      [130.0, 29.0],   // South of Japan
      [145.0, 33.0],   // East of Japan
      [180.0, 42.0],   // Mid Pacific
      [210.0, 42.0],   // Mid Pacific
      [230.0, 36.0],   // Off US Coast
      [241.74, 33.73], // LA
    ],
    type: 'sea',
    label: 'Primary Sea Route (Blocked)',
  },
  {
    id: 'air-reroute',
    from: { coordinates: [121.47, 31.23] },
    to: { coordinates: [241.74, 33.73] },
    type: 'air',
    label: 'AI Air Reroute (Active)',
  },
  {
    id: 'asia-europe',
    from: { coordinates: [121.47, 31.23] },
    to: { coordinates: [4.49, 51.9] },
    path: [
      [121.47, 31.23], // Shanghai
      [119.5, 24.5],   // Taiwan Strait
      [114.0, 15.0],   // South China Sea
      [104.5, 3.0],    // Singapore Strait
      [95.0, 5.0],     // North of Sumatra
      [75.0, 5.0],     // Indian Ocean
      [60.0, 15.0],    // Arabian Sea
      [50.0, 12.0],    // Gulf of Aden
      [43.0, 12.5],    // Bab-el-Mandeb
      [39.0, 21.0],    // Red Sea
      [32.33, 30.57],  // Suez
    ],
    type: 'secondary',
    label: 'Asia–Europe Trade Lane',
  },
  {
    id: 'europe-suez',
    from: { coordinates: [4.49, 51.9] },
    to: { coordinates: [32.33, 30.57] },
    path: [
      [32.33, 30.57],  // Suez
      [30.0, 31.5],    // Mediterranean Sea
      [15.0, 35.0],    // Med
      [0.0, 36.0],     // Alboran Sea
      [-5.5, 35.8],    // Strait of Gibraltar
      [-10.0, 39.0],   // Atlantic off Portugal
      [-6.0, 48.0],    // Bay of Biscay
      [0.0, 50.5],     // English Channel
      [4.49, 51.9],    // Rotterdam
    ],
    type: 'secondary',
    label: 'Europe–Suez Leg',
  },
];

// ---------------------------------------------------------------------------
// Color helpers — returns RGBA arrays for Deck.gl
// ---------------------------------------------------------------------------

const PORT_COLORS: Record<Port['type'], [number, number, number, number]> = {
  origin: [6, 182, 212, 220],       // cyan-500
  destination: [16, 185, 129, 220], // emerald-500
  hub: [100, 116, 139, 200],        // slate-500
  disruption: [239, 68, 68, 220],   // red-500
};

const REROUTED_COLOR: [number, number, number, number] = [52, 211, 153, 230]; // emerald-400

// Free Carto Dark Matter raster tiles
const TILE_URL = 'https://cartodb-basemaps-a.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png';

// ---------------------------------------------------------------------------
// Initial view state — centred on Pacific / Asia trade lane
// ---------------------------------------------------------------------------

const INITIAL_VIEW_STATE = {
  longitude: 10,
  latitude: 30,
  zoom: 2.1,
  pitch: 0,
  bearing: 0,
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const RouteMap: React.FC<RouteMapProps> = ({ activeStep = 1, onSelectRoute }) => {
  const [selectedId, setSelectedId] = useState<string | null>('disruption-shanghai');
  const [activeLayer, setActiveLayer] = useState<'all' | 'disrupted' | 'reroute'>('all');
  const [hoverInfo, setHoverInfo] = useState<{
    x: number;
    y: number;
    port: Port;
  } | null>(null);

  const isRerouted = activeStep >= 6;

  // Reactively override disruption status based on activeStep
  const ports = useMemo<Port[]>(
    () =>
      PORTS.map((p) =>
        p.id === 'disruption-shanghai'
          ? { ...p, status: isRerouted ? 'rerouted' : 'disrupted' }
          : p
      ),
    [isRerouted]
  );

  const selectedPort = ports.find((p) => p.id === selectedId) ?? ports[1];

  // -------------------------------------------------------------------------
  // Arc visibility based on layer filter
  // -------------------------------------------------------------------------

  const visibleArcs = useMemo(() => {
    return ARCS.filter((arc) => {
      if (activeLayer === 'disrupted') return arc.type === 'sea';
      if (activeLayer === 'reroute') return arc.type === 'air';
      return true; // 'all'
    });
  }, [activeLayer]);

  // -------------------------------------------------------------------------
  // Deck.gl Layers
  // -------------------------------------------------------------------------

  const layers = useMemo(() => {
    // --- Base Map (TileLayer) ---
    const tileLayer = new TileLayer({
      id: 'base-map',
      data: TILE_URL,
      minZoom: 0,
      maxZoom: 19,
      tileSize: 256,
      renderSubLayers: (props) => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const bbox: any = props.tile.bbox;

        return new BitmapLayer(props, {
          data: undefined,
          image: props.data,
          bounds: [bbox.west, bbox.south, bbox.east, bbox.north],
        });
      },
    });

    // --- Arc Layer (Air routes) ---
    const arcLayer = new ArcLayer({
      id: 'shipping-arcs',
      data: visibleArcs.filter(d => d.type === 'air'),
      getSourcePosition: (d: ShippingArc) => d.from.coordinates,
      getTargetPosition: (d: ShippingArc) => d.to.coordinates,
      getSourceColor: (): [number, number, number, number] => {
        return [6, 182, 212, 220]; // air color
      },
      getTargetColor: (): [number, number, number, number] => {
        return [16, 185, 129, 220]; // destination color
      },
      getWidth: 3,
      getHeight: 0.6,
      getDashArray: [8, 4],
      dashJustified: true,
      extensions: [],
      pickable: false,
      wrapLongitude: true,
    });

    // --- Path Layer (Sea routes) ---
    const pathLayer = new PathLayer({
      id: 'shipping-paths',
      data: visibleArcs.filter(d => d.path),
      getPath: (d: ShippingArc) => d.path as [number, number][],
      getColor: (d: ShippingArc): [number, number, number, number] => {
        if (d.type === 'sea') return isRerouted ? [51, 65, 85, 80] : [239, 68, 68, 200];
        return [51, 65, 85, 120];
      },
      getWidth: (d: ShippingArc) => (d.type === 'sea' ? 2.5 : 1.5),
      getDashArray: (d: ShippingArc): [number, number] =>
        d.type === 'sea' ? [6, 4] : [4, 4],
      dashJustified: true,
      extensions: [],
      widthMinPixels: 2,
      pickable: false,
      wrapLongitude: true,
    });

    // --- Scatter (Port Pins) ---
    const scatterLayer = new ScatterplotLayer({
      id: 'port-pins',
      data: ports,
      getPosition: (d: Port) => d.coordinates,
      getRadius: (d: Port) => {
        if (d.type === 'disruption') return 80000;
        if (d.id === selectedId) return 70000;
        return 50000;
      },
      getFillColor: (d: Port): [number, number, number, number] => {
        if (d.type === 'disruption') {
          return isRerouted ? REROUTED_COLOR : [239, 68, 68, 230];
        }
        return PORT_COLORS[d.type];
      },
      getLineColor: (d: Port): [number, number, number, number] => {
        if (d.id === selectedId) return [255, 255, 255, 200];
        return [0, 0, 0, 0];
      },
      getLineWidth: (d: Port) => (d.id === selectedId ? 3000 : 0),
      lineWidthMinPixels: 0,
      stroked: true,
      filled: true,
      radiusMinPixels: 6,
      radiusMaxPixels: 18,
      pickable: true,
      autoHighlight: true,
      highlightColor: [255, 255, 255, 60],
      onClick: (info: PickingInfo) => {
        const port = info.object as Port | undefined;
        if (port) {
          setSelectedId(port.id);
          onSelectRoute?.(port.id);
        }
      },
      onHover: (info: PickingInfo) => {
        const port = info.object as Port | undefined;
        setHoverInfo(port ? { x: info.x, y: info.y, port } : null);
      },
      updateTriggers: {
        getFillColor: [isRerouted],
        getRadius: [selectedId],
        getLineColor: [selectedId],
        getLineWidth: [selectedId],
      },
      wrapLongitude: true,
    });

    // --- Text Labels ---
    const textLayer = new TextLayer({
      id: 'port-labels',
      data: ports.filter((p) => p.type !== 'disruption'),
      getPosition: (d: Port) => d.coordinates,
      getText: (d: Port) => d.code,
      getSize: 11,
      getColor: [203, 213, 225, 200], // slate-300
      getAnchor: 'middle',
      getAlignmentBaseline: 'top',
      getPixelOffset: [0, 14],
      fontFamily: 'Inter, sans-serif',
      fontWeight: '600',
      pickable: false,
    });

    return [tileLayer, pathLayer, arcLayer, scatterLayer, textLayer];
  }, [visibleArcs, ports, selectedId, isRerouted, onSelectRoute]);

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="card-surface rounded-xl flex flex-col h-full overflow-hidden border border-outline-variant bg-surface-container-lowest shadow-sm relative">
      {/* Header & Filter Toolbar */}
      <div className="p-unit-md border-b border-outline-variant flex justify-between items-center bg-surface-container-low shrink-0 z-10">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[18px]">map</span>
          <h2 className="text-sm font-semibold text-on-surface">Global Supply Chain Disruption Map</h2>
          <span className="text-[10px] bg-error/10 text-error border border-error/20 px-2 py-0.5 rounded-full font-bold uppercase tracking-widest flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-error animate-ping" />
            Live Telemetry
          </span>
        </div>

        {/* Layer Filters */}
        <div className="flex items-center space-x-1 bg-surface-container-high p-0.5 rounded-lg border border-outline-variant text-[10px]">
          {(
            [
              { id: 'all', label: 'All Trade Lanes', activeClass: 'bg-primary text-white font-bold shadow-xs' },
              { id: 'disrupted', label: 'Disruptions', activeClass: 'bg-error text-white font-bold shadow-xs' },
              { id: 'reroute', label: 'Active Reroutes', activeClass: 'bg-emerald-600 text-white font-bold shadow-xs' },
            ] as const
          ).map(({ id, label, activeClass }) => (
            <button
              key={id}
              onClick={() => setActiveLayer(id)}
              className={`px-2 py-1 rounded font-medium transition-colors ${
                activeLayer === id ? activeClass : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Deck.gl Map Canvas */}
      <div className="relative flex-1 min-h-0">
        <DeckGL
          initialViewState={INITIAL_VIEW_STATE}
          controller={true}
          layers={layers}
          style={{ position: 'absolute', inset: '0' }}
        >
        </DeckGL>

        {/* Hover Tooltip */}
        {hoverInfo && (
          <div
            className="absolute pointer-events-none z-30 bg-slate-900/95 backdrop-blur-md border border-slate-700 px-2.5 py-1.5 rounded-lg text-[11px] text-slate-200 shadow-xl whitespace-nowrap"
            style={{ left: hoverInfo.x + 12, top: hoverInfo.y - 10 }}
          >
            <span className="font-bold text-white">{hoverInfo.port.name}</span>
            <span className="text-slate-400 ml-1.5">({hoverInfo.port.code})</span>
          </div>
        )}

        {/* Selected Port Info Card */}
        {selectedPort && (
          <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-lg p-3 max-w-xs z-20 shadow-xl text-xs space-y-1.5">
            <div className="flex items-center justify-between gap-2">
              <span className="font-bold text-slate-100">{selectedPort.name}</span>
              <span
                className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                  selectedPort.status === 'disrupted'
                    ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                    : selectedPort.status === 'rerouted'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-cyan-500/20 text-cyan-300'
                }`}
              >
                {selectedPort.status === 'rerouted' ? 'Rerouted' : selectedPort.status}
              </span>
            </div>
            <p className="text-[11px] text-slate-300 leading-normal">{selectedPort.details}</p>
            {isRerouted && selectedPort.id === 'disruption-shanghai' && (
              <div className="text-[10px] text-emerald-400 font-semibold pt-0.5 flex items-center gap-1">
                ✈️ Rerouted via Apex Air Freight (ETA 2 Days)
              </div>
            )}
          </div>
        )}

        {/* Legend */}
        <div className="absolute bottom-3 right-3 bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-lg px-2.5 py-2 text-[10px] text-slate-300 space-y-1 z-20 hidden sm:block">
          <div className="flex items-center gap-2">
            <span className="w-4 h-0.5 bg-red-500 inline-block rounded" />
            <span>Blocked Sea Path</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-0.5 bg-cyan-400 inline-block rounded" />
            <span>AI Air Reroute</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block" />
            <span>Origin Port</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block" />
            <span>Destination</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" />
            <span>Disruption Zone</span>
          </div>
        </div>

        {/* Disruption Pulse Beacon (rendered as DOM overlay at approximate screen position) */}
        <DisruptionBeacon isRerouted={isRerouted} />
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Small sub-component: animated beacon overlay (decorative, positioned center-right)
// ---------------------------------------------------------------------------

function DisruptionBeacon({ isRerouted }: { isRerouted: boolean }) {
  // Approximate screen position for the East China Sea disruption point —
  // we can't get exact pixel from Deck.gl without project(), so we use a
  // visual hint near the right side of the map
  return (
    <div
      className="absolute pointer-events-none z-20"
      style={{ right: '18%', top: '38%' }}
    >
      <span
        className={`absolute inline-flex h-7 w-7 rounded-full opacity-60 -translate-x-1/2 -translate-y-1/2 ${
          isRerouted ? 'bg-emerald-400 animate-ping' : 'bg-red-500 animate-ping'
        }`}
      />
    </div>
  );
}

export default RouteMap;
