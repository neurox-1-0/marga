'use client';

import React, { useState } from 'react';

interface RouteMapProps {
  activeStep?: number;
  onSelectRoute?: (routeId: string) => void;
}

interface Waypoint {
  id: string;
  name: string;
  code: string;
  x: number; // Percentage on map canvas
  y: number; // Percentage on map canvas
  type: 'origin' | 'destination' | 'disruption' | 'hub';
  status: 'normal' | 'disrupted' | 'rerouted';
  details: string;
}

export const RouteMap: React.FC<RouteMapProps> = ({ activeStep = 1, onSelectRoute }) => {
  const [selectedPin, setSelectedPin] = useState<string | null>('disruption-shanghai');
  const [activeLayer, setActiveLayer] = useState<'all' | 'disrupted' | 'reroute'>('all');

  // Key supply chain nodes
  const waypoints: Waypoint[] = [
    {
      id: 'port-shanghai',
      name: 'Port of Shanghai',
      code: 'CNSHA',
      x: 76,
      y: 45,
      type: 'origin',
      status: 'disrupted',
      details: 'Origin Port · 8 Impacted Shipments ($1.25M Inventory)',
    },
    {
      id: 'disruption-shanghai',
      name: 'East China Sea Disruption',
      code: 'TYPHOON-01',
      x: 79,
      y: 43,
      type: 'disruption',
      status: activeStep >= 6 ? 'rerouted' : 'disrupted',
      details: 'Typhoon Alert · +7 Days Maritime Delay · Active Typhoon Warning',
    },
    {
      id: 'port-lax',
      name: 'Port of Los Angeles',
      code: 'USLAX',
      x: 22,
      y: 40,
      type: 'destination',
      status: 'normal',
      details: 'Destination Hub · Destination for PO-101 & PO-102',
    },
    {
      id: 'port-suez',
      name: 'Suez Canal Hub',
      code: 'EGSUE',
      x: 58,
      y: 48,
      type: 'hub',
      status: 'normal',
      details: 'Middle East Transit Channel · Flowing Normal',
    },
    {
      id: 'port-rotterdam',
      name: 'Port of Rotterdam',
      code: 'NLRTM',
      x: 48,
      y: 30,
      type: 'hub',
      status: 'normal',
      details: 'European Gateway · Flowing Normal',
    },
  ];

  const selectedPoint = waypoints.find((w) => w.id === selectedPin) || waypoints[1];

  return (
    <div className="card-surface rounded-xl flex flex-col h-full overflow-hidden border border-outline-variant bg-surface-container-lowest shadow-sm relative">
      {/* Map Header & Filter Toolbar */}
      <div className="p-unit-md border-b border-outline-variant flex justify-between items-center bg-surface-container-low">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[18px]">map</span>
          <h2 className="text-sm font-semibold text-on-surface">Global Supply Chain Disruption Map</h2>
          <span className="text-[10px] bg-error/10 text-error border border-error/20 px-2 py-0.5 rounded-full font-bold uppercase tracking-widest flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-error animate-ping"></span>
            Live Telemetry
          </span>
        </div>

        {/* Layer Filters */}
        <div className="flex items-center space-x-1 bg-surface-container-high p-0.5 rounded-lg border border-outline-variant text-[10px]">
          <button
            onClick={() => setActiveLayer('all')}
            className={`px-2 py-1 rounded font-medium transition-colors ${
              activeLayer === 'all'
                ? 'bg-primary text-white font-bold shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            All Trade Lanes
          </button>
          <button
            onClick={() => setActiveLayer('disrupted')}
            className={`px-2 py-1 rounded font-medium transition-colors ${
              activeLayer === 'disrupted'
                ? 'bg-error text-white font-bold shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Disruptions
          </button>
          <button
            onClick={() => setActiveLayer('reroute')}
            className={`px-2 py-1 rounded font-medium transition-colors ${
              activeLayer === 'reroute'
                ? 'bg-emerald-600 text-white font-bold shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Active Reroutes
          </button>
        </div>
      </div>

      {/* SVG Vector World Canvas */}
      <div className="relative flex-1 bg-[#0b1329] min-h-[300px] overflow-hidden select-none">
        {/* Background Grid Pattern */}
        <div
          className="absolute inset-0 opacity-15 pointer-events-none"
          style={{
            backgroundImage: `radial-gradient(circle, #3b82f6 1px, transparent 1px)`,
            backgroundSize: '24px 24px',
          }}
        ></div>

        {/* Vector SVG Routes & Shipping Lanes */}
        <svg className="w-full h-full absolute inset-0 pointer-events-none" viewBox="0 0 1000 500" preserveAspectRatio="none">
          <defs>
            {/* Gradient for Air Reroute Arc */}
            <linearGradient id="airRerouteGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#3b82f6" stopOpacity="1" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0.9" />
            </linearGradient>

            {/* Glowing filter for active paths */}
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Continent Outline Visual Markers (Stylized vector reference lines) */}
          <path
            d="M 150 150 Q 250 120 350 180 T 450 300"
            fill="none"
            stroke="#1e293b"
            strokeWidth="30"
            strokeLinecap="round"
            opacity="0.4"
          />
          <path
            d="M 650 130 Q 750 150 850 220 T 780 380"
            fill="none"
            stroke="#1e293b"
            strokeWidth="45"
            strokeLinecap="round"
            opacity="0.4"
          />

          {/* 1. Primary Sea Route: Shanghai (760, 225) ➔ Los Angeles (220, 200) */}
          {activeLayer !== 'reroute' && (
            <g>
              {/* Blocked/Disrupted Ocean Path */}
              <path
                d="M 760 225 C 600 120, 400 120, 220 200"
                fill="none"
                stroke={activeStep >= 6 ? '#334155' : '#ef4444'}
                strokeWidth="3"
                strokeDasharray={activeStep >= 6 ? '4 4' : '6 6'}
                opacity={activeStep >= 6 ? 0.4 : 0.8}
              />
            </g>
          )}

          {/* 2. Alternative Air Reroute Path: Shanghai (760, 225) ➔ Direct Flight Arc ➔ LA (220, 200) */}
          {(activeLayer === 'all' || activeLayer === 'reroute') && (
            <g>
              <path
                d="M 760 225 Q 490 60 220 200"
                fill="none"
                stroke="url(#airRerouteGrad)"
                strokeWidth="3.5"
                filter="url(#glow)"
                strokeDasharray="8 4"
                className="animate-[dash_20s_linear_infinite]"
              />
              {/* Flight Icon Animation Indicator along arc */}
              <circle cx="490" cy="115" r="5" fill="#06b6d4" className="animate-ping" />
              <circle cx="490" cy="115" r="3" fill="#ffffff" />
            </g>
          )}

          {/* Secondary Trade Routes (Europe / Asia) */}
          <path
            d="M 480 150 Q 580 240 760 225"
            fill="none"
            stroke="#334155"
            strokeWidth="1.5"
            strokeDasharray="4 4"
            opacity="0.4"
          />
        </svg>

        {/* Interactive Waypoint Pins */}
        {waypoints.map((point) => {
          const isSelected = selectedPin === point.id;
          const isDisruption = point.type === 'disruption';
          const isRerouted = point.status === 'rerouted';

          return (
            <div
              key={point.id}
              onClick={() => {
                setSelectedPin(point.id);
                if (onSelectRoute) onSelectRoute(point.id);
              }}
              style={{ left: `${point.x}%`, top: `${point.y}%` }}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer z-10 group"
            >
              {/* Disruption Radar Beacon */}
              {isDisruption && (
                <div className="relative flex items-center justify-center">
                  <span
                    className={`absolute inline-flex h-8 w-8 rounded-full opacity-75 ${
                      isRerouted ? 'bg-emerald-400 animate-ping' : 'bg-red-500 animate-ping'
                    }`}
                  ></span>
                  <div
                    className={`relative w-5 h-5 rounded-full border-2 flex items-center justify-center text-[10px] font-bold shadow-lg ${
                      isRerouted
                        ? 'bg-emerald-500 border-emerald-300 text-slate-950'
                        : 'bg-red-600 border-red-300 text-white'
                    }`}
                  >
                    {isRerouted ? '✓' : '!'}
                  </div>
                </div>
              )}

              {/* Standard Port Pin */}
              {!isDisruption && (
                <div
                  className={`w-3.5 h-3.5 rounded-full border-2 transition-all group-hover:scale-125 ${
                    point.type === 'origin'
                      ? 'bg-cyan-400 border-cyan-200 shadow-cyan-500/50'
                      : point.type === 'destination'
                      ? 'bg-emerald-400 border-emerald-200 shadow-emerald-500/50'
                      : 'bg-slate-400 border-slate-200'
                  } ${isSelected ? 'ring-4 ring-cyan-400/30 scale-125' : ''}`}
                ></div>
              )}

              {/* Hover Badge */}
              <div className="absolute left-1/2 -bottom-7 transform -translate-x-1/2 whitespace-nowrap bg-slate-900/90 backdrop-blur-md border border-slate-700 px-2 py-0.5 rounded text-[10px] font-medium text-slate-200 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-20 shadow-md">
                {point.name} ({point.code})
              </div>
            </div>
          );
        })}

        {/* Selected Pin Info Card Floating Overlay */}
        {selectedPoint && (
          <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-lg p-3 max-w-xs z-20 shadow-xl text-xs space-y-1">
            <div className="flex items-center justify-between gap-2">
              <span className="font-bold text-slate-100">{selectedPoint.name}</span>
              <span
                className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                  selectedPoint.status === 'disrupted'
                    ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                    : selectedPoint.status === 'rerouted'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-cyan-500/20 text-cyan-300'
                }`}
              >
                {selectedPoint.status}
              </span>
            </div>
            <p className="text-[11px] text-slate-300 leading-normal">{selectedPoint.details}</p>
            {activeStep >= 6 && selectedPoint.id === 'disruption-shanghai' && (
              <div className="text-[10px] text-emerald-400 font-semibold pt-1 flex items-center gap-1">
                <span>✈️ Rerouted via Apex Air Freight (ETA 2 Days)</span>
              </div>
            )}
          </div>
        )}

        {/* Map Legend */}
        <div className="absolute bottom-3 right-3 bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-lg px-2.5 py-2 text-[10px] text-slate-300 space-y-1 z-20 hidden sm:block">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-0.5 bg-red-500 inline-block"></span>
            <span>Blocked Sea Path</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-0.5 bg-cyan-400 inline-block"></span>
            <span>AI Air Reroute</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 inline-block"></span>
            <span>Origin / Hub</span>
          </div>
        </div>
      </div>
    </div>
  );
};
