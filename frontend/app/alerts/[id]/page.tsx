"use client";

import { useState } from "react";
import Link from "next/link";

export default function AlertDetailsPage() {
  const [decision, setDecision] = useState<null | 'approved' | 'rejected' | 'redirected' | 'info'>(null);
  const [redirectOption, setRedirectOption] = useState<null | string>(null);
  const [infoLoading, setInfoLoading] = useState(true);

  const handleInfoClick = () => {
    setDecision('info');
    setInfoLoading(true);
    setTimeout(() => {
      setInfoLoading(false);
    }, 2000);
  };

  const renderDecisionContent = () => {
    if (decision === 'approved') {
      return (
        <div className="flex flex-col items-center justify-center text-center space-y-4 py-4">
          <span className="material-symbols-outlined text-emerald-500 text-[48px]">check_circle</span>
          <div>
            <h2 className="text-on-surface text-xl font-bold">Reroute Approved</h2>
            <p className="text-on-surface-variant text-sm mt-2">
              Air-freight booking confirmed via FedEx Freight. ETA: 2 days.
            </p>
          </div>
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 w-full">
            <p className="text-emerald-700 text-sm font-medium">
              Event ID MRG-2024-0847 has been logged. ERP records updated.
            </p>
          </div>
          <Link href="/" className="w-full bg-surface-container-low hover:bg-surface-container-high transition-colors text-on-surface border border-outline-variant rounded-lg py-3 font-medium flex items-center justify-center mt-4">
            <span className="material-symbols-outlined text-[16px] mr-2">arrow_back</span> Back to Dashboard
          </Link>
        </div>
      );
    }

    if (decision === 'rejected') {
      return (
        <div className="flex flex-col items-center justify-center text-center space-y-4 py-4">
          <span className="material-symbols-outlined text-error text-[48px]">cancel</span>
          <div>
            <h2 className="text-on-surface text-xl font-bold">Action Rejected</h2>
            <p className="text-on-surface-variant text-sm mt-2">
              No action taken. This disruption has been logged and closed.
            </p>
          </div>
          <Link href="/alerts" className="w-full bg-surface-container-low hover:bg-surface-container-high transition-colors text-on-surface border border-outline-variant rounded-lg py-3 font-medium flex items-center justify-center mt-4">
            <span className="material-symbols-outlined text-[16px] mr-2">arrow_back</span> Back to Alerts
          </Link>
        </div>
      );
    }

    if (decision === 'redirected') {
      if (redirectOption) {
        return (
          <div className="flex flex-col items-center justify-center text-center space-y-4 py-4">
            <span className="material-symbols-outlined text-primary text-[48px]">check_circle</span>
            <div>
              <h2 className="text-on-surface text-xl font-bold">Alternative Selected</h2>
              <p className="text-on-surface-variant text-sm mt-2">
                {redirectOption} booked successfully.
              </p>
            </div>
            <Link href="/" className="w-full bg-surface-container-low hover:bg-surface-container-high transition-colors text-on-surface border border-outline-variant rounded-lg py-3 font-medium flex items-center justify-center mt-4">
              <span className="material-symbols-outlined text-[16px] mr-2">arrow_back</span> Back to Dashboard
            </Link>
          </div>
        );
      }

      return (
        <div className="space-y-4">
          <h2 className="text-on-surface text-lg font-bold mb-4">Select Alternative</h2>
          <div 
            onClick={() => setRedirectOption("Rail freight")}
            className="bg-surface-container-lowest border border-outline-variant rounded-lg p-3 cursor-pointer hover:border-primary transition-colors"
          >
            <p className="text-on-surface font-medium text-sm">Rail Freight via CN Rail · $2,100 · ETA 6 days</p>
          </div>
          <div 
            onClick={() => setRedirectOption("Alt Port routing")}
            className="bg-surface-container-lowest border border-outline-variant rounded-lg p-3 cursor-pointer hover:border-primary transition-colors"
          >
            <p className="text-on-surface font-medium text-sm">Alt Port — Oakland · $3,200 · ETA 3 days</p>
          </div>
          <button 
            onClick={() => setDecision(null)}
            className="w-full mt-4 bg-transparent hover:bg-surface-container-high text-on-surface-variant border border-outline-variant py-2 rounded-lg text-sm transition-colors font-medium"
          >
            Cancel
          </button>
        </div>
      );
    }

    if (decision === 'info') {
      return (
        <div className="flex flex-col items-center justify-center text-center space-y-6 py-4">
          <span className={`material-symbols-outlined text-amber-500 text-[48px] ${infoLoading ? 'animate-spin' : ''}`}>sync</span>
          
          {infoLoading ? (
            <div className="space-y-4 w-full">
              <h2 className="text-on-surface text-xl font-bold">Re-querying Systems...</h2>
              <ul className="text-left space-y-2 text-sm text-on-surface-variant animate-pulse font-medium">
                <li className="flex items-center"><span className="text-outline-variant mr-2">●</span> ERP: Re-checking PO #4471 match...</li>
                <li className="flex items-center"><span className="text-outline-variant mr-2">●</span> Project44: Refreshing freight quotes...</li>
                <li className="flex items-center"><span className="text-outline-variant mr-2">●</span> AIS Feed: Confirming vessel status...</li>
              </ul>
            </div>
          ) : (
            <div className="space-y-4 w-full">
              <h2 className="text-on-surface text-xl font-bold">Data Refreshed</h2>
              <p className="text-on-surface-variant text-sm">
                All sources confirmed. No changes to original recommendation.
              </p>
              <button 
                onClick={() => setDecision(null)}
                className="w-full bg-surface-container-low hover:bg-surface-container-high transition-colors text-on-surface border border-outline-variant rounded-lg py-3 font-medium flex items-center justify-center mt-4"
              >
                <span className="material-symbols-outlined text-[16px] mr-2">arrow_back</span> Back to Options
              </button>
            </div>
          )}
        </div>
      );
    }

    // Default decision = null
    return (
      <>
        <h2 className="text-on-surface text-sm font-semibold mb-1">Your Decision</h2>
        <p className="text-on-surface-variant text-[10px] mb-6 font-medium">
          Review the recommendation and choose an action. This cannot be undone.
        </p>

        <div className="space-y-3">
          <button 
            onClick={() => setDecision('approved')}
            className="w-full bg-primary hover:brightness-110 transition-all text-white rounded-lg py-3 font-semibold flex items-center justify-center shadow-sm text-sm"
          >
            <span className="material-symbols-outlined text-[18px] mr-2">check</span> Approve — Book Air-Freight Reroute
          </button>
          
          <div className="grid grid-cols-2 gap-3">
            <button 
              onClick={() => setDecision('rejected')}
              className="bg-transparent hover:bg-error/10 transition-colors text-on-surface-variant hover:text-error hover:border-error border border-outline-variant rounded-lg py-2 font-medium flex items-center justify-center text-sm"
            >
              <span className="material-symbols-outlined text-[16px] mr-2">close</span> Reject
            </button>
            <button 
              onClick={() => setDecision('redirected')}
              className="bg-transparent hover:bg-primary/10 transition-colors text-on-surface-variant hover:text-primary hover:border-primary border border-outline-variant rounded-lg py-2 font-medium flex items-center justify-center text-sm"
            >
              <span className="material-symbols-outlined text-[16px] mr-2">swap_horiz</span> Redirect
            </button>
          </div>
          
          <button 
            onClick={handleInfoClick}
            className="w-full bg-transparent hover:bg-surface-container-high transition-colors text-on-surface-variant border border-outline-variant rounded-lg py-2 font-bold flex items-center justify-center text-[10px] uppercase tracking-widest"
          >
            <span className="material-symbols-outlined text-[16px] mr-2">help</span> Request More Info
          </button>
        </div>

        <div className="mt-6 bg-surface-container-low rounded-lg p-3 flex items-start space-x-2">
          <span className="material-symbols-outlined text-on-surface-variant text-[16px] shrink-0">schedule</span>
          <p className="text-[10px] text-on-surface-variant font-medium">
            No response will escalate this alert — it will never auto-approve.
          </p>
        </div>
      </>
    );
  };

  return (
    <main className="ml-64 mt-16 p-unit-lg h-[calc(100vh-64px)] overflow-y-auto">
      <div className="space-y-6 max-w-7xl mx-auto pb-8">
        
        {/* Top: Back navigation */}
        <div>
          <Link href="/alerts" className="inline-flex items-center text-primary hover:brightness-110 transition-colors mb-4 text-[12px] font-bold uppercase tracking-widest">
            <span className="material-symbols-outlined text-[16px] mr-1">arrow_back</span>
            Back to Alerts
          </Link>
          <div className="flex items-center space-x-4">
            <h1 className="text-on-surface font-headline-lg">Port Strike — Shanghai Terminal 2</h1>
            <span className="bg-error/10 text-error text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full">
              High Risk
            </span>
          </div>
        </div>

        {/* Main layout */}
        <div className="flex space-x-unit-lg">
          
          {/* Left column */}
          <div className="flex-1 space-y-unit-lg">
            
            {/* Card 1: Disruption Summary */}
            <div className="card-surface rounded-xl p-unit-md space-y-4">
              <div className="flex items-center space-x-2">
                <span className="material-symbols-outlined text-amber-500 text-[20px]">warning</span>
                <h2 className="text-on-surface text-sm font-semibold">Disruption Summary</h2>
              </div>
              
              <div className="grid grid-cols-2 gap-y-4 gap-x-6">
                <div>
                  <p className="text-on-surface-variant text-[10px] font-bold uppercase tracking-widest">Event</p>
                  <p className="text-on-surface text-[11px] font-medium mt-1">Port Strike — Shanghai Terminal 2</p>
                </div>
                <div>
                  <p className="text-on-surface-variant text-[10px] font-bold uppercase tracking-widest">Affected Route</p>
                  <p className="text-on-surface text-[11px] font-medium mt-1">Shanghai → Los Angeles (Trans-Pacific)</p>
                </div>
                <div>
                  <p className="text-on-surface-variant text-[10px] font-bold uppercase tracking-widest">Estimated Delay</p>
                  <p className="text-on-surface text-[11px] font-medium mt-1">5–7 business days</p>
                </div>
                <div>
                  <p className="text-on-surface-variant text-[10px] font-bold uppercase tracking-widest">Detected</p>
                  <p className="text-on-surface text-[11px] font-medium mt-1">Today at 09:14 AM via Maritime AIS Feed</p>
                </div>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                <p className="text-amber-700 text-[10px] font-medium">
                  Agent confidence: High · All data sourced from live AIS feed + ERP match
                </p>
              </div>
            </div>

            {/* Card 2: Exposure Analysis */}
            <div className="card-surface rounded-xl p-unit-md space-y-4">
              <h2 className="text-on-surface text-sm font-semibold">Exposure Analysis</h2>
              
              <div className="grid grid-cols-3 gap-unit-md">
                <div className="bg-surface-container-low rounded-lg p-unit-md">
                  <p className="text-on-surface-variant text-[10px] font-bold uppercase tracking-widest mb-1">POs Affected</p>
                  <p className="text-on-surface text-2xl font-bold">8</p>
                </div>
                <div className="bg-surface-container-low rounded-lg p-unit-md">
                  <p className="text-on-surface-variant text-[10px] font-bold uppercase tracking-widest mb-1">Inventory at Risk</p>
                  <p className="text-error text-2xl font-bold">$184,000</p>
                </div>
                <div className="bg-surface-container-low rounded-lg p-unit-md">
                  <p className="text-on-surface-variant text-[10px] font-bold uppercase tracking-widest mb-1">Stockout Risk</p>
                  <p className="text-error text-2xl font-bold">High</p>
                </div>
              </div>

              <div className="border border-outline-variant rounded-lg overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-outline-variant text-[10px] font-bold text-on-surface-variant uppercase tracking-widest bg-surface-container-low">
                      <th className="px-3 py-2 font-medium">PO Number</th>
                      <th className="px-3 py-2 font-medium">Category</th>
                      <th className="px-3 py-2 font-medium text-right">Value (USD)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant">
                    <tr className="hover:bg-surface-container-lowest transition-colors">
                      <td className="p-3 text-on-surface text-[11px] font-medium">PO #4471</td>
                      <td className="p-3 text-on-surface-variant text-[11px]">Electronics</td>
                      <td className="p-3 text-on-surface text-[11px] font-medium text-right">$42,000</td>
                    </tr>
                    <tr className="hover:bg-surface-container-lowest transition-colors">
                      <td className="p-3 text-on-surface text-[11px] font-medium">PO #4489</td>
                      <td className="p-3 text-on-surface-variant text-[11px]">Auto Parts</td>
                      <td className="p-3 text-on-surface text-[11px] font-medium text-right">$67,000</td>
                    </tr>
                    <tr className="hover:bg-surface-container-lowest transition-colors">
                      <td className="p-3 text-on-surface text-[11px] font-medium">PO #4502</td>
                      <td className="p-3 text-on-surface-variant text-[11px]">Pharma</td>
                      <td className="p-3 text-on-surface text-[11px] font-medium text-right">$75,000</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="bg-error/5 border border-error/20 rounded-lg p-3">
                <p className="text-error text-[10px] font-medium">
                  3 open customer orders depend on this stock. Production line impact estimated at 2 days.
                </p>
              </div>
            </div>

            {/* Card 3: Recommended vs Alternative */}
            <div className="card-surface rounded-xl p-unit-md space-y-4">
              <h2 className="text-on-surface text-sm font-semibold">Recommended vs Alternative</h2>
              
              <div className="grid grid-cols-2 gap-unit-md">
                {/* Left - RECOMMENDED */}
                <div className="bg-emerald-50 border-2 border-emerald-400 rounded-xl p-unit-md flex flex-col justify-between">
                  <div>
                    <span className="text-emerald-600 text-[10px] font-bold tracking-widest mb-2 block uppercase">Recommended</span>
                    <h3 className="text-on-surface font-bold text-sm">Air-Freight Reroute</h3>
                    <p className="text-on-surface-variant text-[11px] mt-2 leading-relaxed font-medium">
                      Via FedEx Freight<br />
                      ETA: 2 days<br />
                      Shanghai Pudong → LAX
                    </p>
                  </div>
                  <div className="mt-4 pt-4 border-t border-emerald-200 flex justify-between items-end">
                    <div>
                      <span className="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Cost Impact</span>
                      <p className="text-emerald-700 text-2xl font-bold">$4,500</p>
                    </div>
                  </div>
                </div>

                {/* Right - ALTERNATIVE */}
                <div className="bg-surface-container-low border border-outline-variant rounded-xl p-unit-md flex flex-col justify-between">
                  <div>
                    <span className="text-on-surface-variant text-[10px] font-bold tracking-widest mb-2 block uppercase">Alternative</span>
                    <h3 className="text-on-surface font-bold text-sm">Accept Delay</h3>
                    <p className="text-on-surface-variant text-[11px] mt-2 leading-relaxed font-medium">
                      Stockout cost estimate<br />
                      5–7 day delay<br />
                      Production line impact
                    </p>
                  </div>
                  <div className="mt-4 pt-4 border-t border-outline-variant flex justify-between items-end">
                    <div>
                      <span className="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Cost Impact</span>
                      <p className="text-error text-2xl font-bold">$28,000 <span className="text-xs font-normal opacity-80">est.</span></p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-start space-x-2">
                <span className="material-symbols-outlined text-[16px] text-on-surface-variant mt-0.5 shrink-0">info</span>
                <p className="text-[10px] text-on-surface-variant font-medium">
                  Cost comparison based on inventory value, lead time impact, and historical stockout data.
                </p>
              </div>
            </div>
            
          </div>

          {/* Right column */}
          <div className="w-80 space-y-unit-lg">
            
            {/* Card 1: Agent Decision */}
            <div className="card-surface rounded-xl p-unit-md transition-all duration-300">
              {renderDecisionContent()}
            </div>

            {/* Card 2: Data Sources Timeline */}
            <div className="card-surface rounded-xl p-unit-md relative">
              <h2 className="text-on-surface text-sm font-semibold mb-4 relative z-10">Data Sources</h2>
              
              <div className="relative">
                <div className="timeline-line" style={{ top: '0px' }}></div>
                <div className="space-y-6 relative z-10">
                  <div className="relative pl-8">
                    <div className="absolute w-2.5 h-2.5 bg-emerald-500 rounded-full left-[7px] top-1 shadow-[0_0_8px_rgba(16,185,129,0.8)] ring-2 ring-surface-container-lowest"></div>
                    <p className="text-on-surface-variant text-[10px] font-mono uppercase tracking-widest block mb-1">14:02 UTC</p>
                    <h4 className="text-on-surface text-[11px] font-bold">Maritime AIS Feed</h4>
                    <p className="text-on-surface-variant text-[10px] font-medium mt-1">Vessel delay confirmed</p>
                  </div>
                  
                  <div className="relative pl-8">
                    <div className="absolute w-2.5 h-2.5 bg-emerald-500 rounded-full left-[7px] top-1 shadow-[0_0_8px_rgba(16,185,129,0.8)] ring-2 ring-surface-container-lowest"></div>
                    <p className="text-on-surface-variant text-[10px] font-mono uppercase tracking-widest block mb-1">14:15 UTC</p>
                    <h4 className="text-on-surface text-[11px] font-bold">ERP (SAP)</h4>
                    <p className="text-on-surface-variant text-[10px] font-medium mt-1">8 POs matched, $184,000 exposure</p>
                  </div>
                  
                  <div className="relative pl-8">
                    <div className="absolute w-2.5 h-2.5 bg-emerald-500 rounded-full left-[7px] top-1 shadow-[0_0_8px_rgba(16,185,129,0.8)] ring-2 ring-surface-container-lowest"></div>
                    <p className="text-on-surface-variant text-[10px] font-mono uppercase tracking-widest block mb-1">14:22 UTC</p>
                    <h4 className="text-on-surface text-[11px] font-bold">Project44 Freight API</h4>
                    <p className="text-on-surface-variant text-[10px] font-medium mt-1">Air-freight quote: $4,500</p>
                  </div>
                  
                  <div className="relative pl-8">
                    <div className="absolute w-2.5 h-2.5 bg-amber-500 rounded-full left-[7px] top-1 ring-2 ring-surface-container-lowest"></div>
                    <p className="text-on-surface-variant text-[10px] font-mono uppercase tracking-widest block mb-1">14:23 UTC</p>
                    <h4 className="text-on-surface text-[11px] font-bold">Cost Engine</h4>
                    <p className="text-on-surface-variant text-[10px] font-medium mt-1">Stockout estimate: $28,000 (approximate)</p>
                  </div>
                </div>
              </div>

              <div className="border-t border-outline-variant pt-4 mt-6">
                <p className="text-on-surface-variant font-bold text-[10px] uppercase tracking-widest">
                  Logged at 09:14 AM · Event ID: MRG-2024-0847
                </p>
              </div>
            </div>
            
          </div>
        </div>
        
      </div>
    </main>
  );
}
