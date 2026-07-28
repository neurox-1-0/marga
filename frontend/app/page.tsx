export default function HomePage() {
  return (
    <main className="ml-64 mt-16 p-unit-lg flex space-x-unit-lg h-[calc(100vh-64px)] overflow-hidden">
      {/* Left Panel: Stats & Map */}
      <div className="flex-1 space-y-unit-lg overflow-y-auto pr-2 pb-8">
        
        {/* Stat Cards Row */}
        <div className="grid grid-cols-4 gap-unit-md">
          <div className="card-surface p-unit-md rounded-xl flex flex-col justify-between h-36">
            <div className="flex justify-between items-center text-on-surface-variant mb-4">
              <span className="text-[10px] font-bold uppercase tracking-widest">Active Disruptions</span>
              <span className="material-symbols-outlined text-amber-600 text-[18px]">warning</span>
            </div>
            <div className="flex items-end justify-between">
              <div>
                <div className="text-2xl font-bold text-on-surface leading-none">3</div>
                <div className="text-[10px] text-amber-600 mt-1 flex items-center">
                  <span className="material-symbols-outlined text-[12px] mr-1">trending_up</span>
                  +1 Since yesterday
                </div>
              </div>
              <div className="flex items-end space-x-0.5 h-8">
                <div className="sparkline-bar bg-amber-500/20 h-2"></div>
                <div className="sparkline-bar bg-amber-500/20 h-4"></div>
                <div className="sparkline-bar bg-amber-500/40 h-3"></div>
                <div className="sparkline-bar bg-amber-500/60 h-6"></div>
                <div className="sparkline-bar bg-amber-500 h-8"></div>
              </div>
            </div>
          </div>

          <div className="card-surface p-unit-md rounded-xl flex flex-col justify-between h-36">
            <div className="flex justify-between items-center text-on-surface-variant mb-4">
              <span className="text-[10px] font-bold uppercase tracking-widest">In Transit Risk</span>
              <span className="material-symbols-outlined text-primary text-[18px]">package_2</span>
            </div>
            <div className="flex items-end justify-between">
              <div>
                <div className="text-2xl font-bold text-on-surface leading-none">1,243</div>
                <div className="text-[10px] text-emerald-600 mt-1 flex items-center">
                  <span className="material-symbols-outlined text-[12px] mr-1">trending_down</span>
                  -8.9% Improvement
                </div>
              </div>
              <div className="flex items-end space-x-0.5 h-8">
                <div className="sparkline-bar bg-primary/20 h-6"></div>
                <div className="sparkline-bar bg-primary/20 h-8"></div>
                <div className="sparkline-bar bg-primary/40 h-5"></div>
                <div className="sparkline-bar bg-primary/60 h-4"></div>
                <div className="sparkline-bar bg-primary h-3"></div>
              </div>
            </div>
          </div>

          <div className="card-surface p-unit-md rounded-xl flex flex-col justify-between h-36">
            <div className="flex justify-between items-center text-on-surface-variant mb-4">
              <span className="text-[10px] font-bold uppercase tracking-widest">Est. Exposure</span>
              <span className="material-symbols-outlined text-error text-[18px]">payments</span>
            </div>
            <div className="flex items-end justify-between">
              <div>
                <div className="text-2xl font-bold text-on-surface leading-none">$284k</div>
                <div className="text-[10px] text-error mt-1 flex items-center">
                  <span className="material-symbols-outlined text-[12px] mr-1">trending_up</span>
                  +12.5% vs avg
                </div>
              </div>
              <div className="flex items-end space-x-0.5 h-8">
                <div className="sparkline-bar bg-error/20 h-2"></div>
                <div className="sparkline-bar bg-error/20 h-3"></div>
                <div className="sparkline-bar bg-error/40 h-5"></div>
                <div className="sparkline-bar bg-error/60 h-7"></div>
                <div className="sparkline-bar bg-error h-8"></div>
              </div>
            </div>
          </div>

          <div className="card-surface p-unit-md rounded-xl flex flex-col justify-between h-36">
            <div className="flex justify-between items-center text-on-surface-variant mb-4">
              <span className="text-[10px] font-bold uppercase tracking-widest">SLA Health</span>
              <span className="material-symbols-outlined text-emerald-600 text-[18px]">verified</span>
            </div>
            <div className="flex items-end justify-between">
              <div>
                <div className="text-2xl font-bold text-on-surface leading-none">94.2%</div>
                <div className="text-[10px] text-emerald-600 mt-1 flex items-center">
                  <span className="material-symbols-outlined text-[12px] mr-1">check_circle</span>
                  Target: 95%
                </div>
              </div>
              <div className="flex items-end space-x-0.5 h-8">
                <div className="sparkline-bar bg-emerald-500/20 h-7"></div>
                <div className="sparkline-bar bg-emerald-500/20 h-6"></div>
                <div className="sparkline-bar bg-emerald-500/40 h-8"></div>
                <div className="sparkline-bar bg-emerald-500/60 h-7"></div>
                <div className="sparkline-bar bg-emerald-500 h-8"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Map & Routes Grid */}
        <div className="grid grid-cols-3 gap-unit-lg h-[460px]">
          {/* Top Routes Risk */}
          <div className="card-surface rounded-xl flex flex-col col-span-3">
            <div className="p-unit-md border-b border-outline-variant flex justify-between items-center bg-surface-container-low rounded-t-xl">
              <h2 className="text-sm font-semibold text-on-surface">Active Disruptions</h2>
              <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded-full font-bold uppercase tracking-widest">Live Heat</span>
            </div>
            <div className="p-unit-md space-y-unit-md flex-1">
              {/* Route 1 */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-[11px]">
                  <span className="font-medium text-on-surface">Shanghai → Los Angeles</span>
                  <span className="text-amber-600 font-bold">78% Risk</span>
                </div>
                <div className="h-1.5 bg-surface-container-low rounded-full overflow-hidden">
                  <div className="h-full bg-amber-500 w-[78%]"></div>
                </div>
                <div className="flex justify-between text-[9px] text-on-surface-variant">
                  <span className="font-medium">Awaiting Approval</span>
                  <span className="font-medium">8 Shipments</span>
                </div>
              </div>
              
              {/* Route 2 */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-[11px]">
                  <span className="font-medium text-on-surface">Kaohsiung → Long Beach</span>
                  <span className="text-primary font-bold">58% Risk</span>
                </div>
                <div className="h-1.5 bg-surface-container-low rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-[58%]"></div>
                </div>
                <div className="flex justify-between text-[9px] text-on-surface-variant">
                  <span className="font-medium">Identifying Exposure</span>
                  <span className="font-medium">14 Shipments</span>
                </div>
              </div>
              
              {/* Route 3 */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-[11px]">
                  <span className="font-medium text-on-surface">Rotterdam → Singapore</span>
                  <span className="text-on-surface-variant font-bold">36% Risk</span>
                </div>
                <div className="h-1.5 bg-surface-container-low rounded-full overflow-hidden">
                  <div className="h-full bg-outline-variant w-[36%]"></div>
                </div>
                <div className="flex justify-between text-[9px] text-on-surface-variant">
                  <span className="font-medium">Monitoring</span>
                  <span className="font-medium">4 Shipments</span>
                </div>
              </div>
              <button className="w-full mt-4 py-2 border border-outline-variant rounded-lg text-[11px] text-on-surface font-semibold hover:bg-surface-container-low transition-colors">
                View All Disruptions
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Row: Recent/Upcoming */}
        <div className="grid grid-cols-2 gap-unit-lg pb-unit-lg">
          <div className="card-surface rounded-xl">
            <div className="p-unit-md border-b border-outline-variant flex justify-between items-center bg-surface-container-low rounded-t-xl">
              <h2 className="text-sm font-semibold text-on-surface">Upcoming Milestones</h2>
              <span className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">Next 48h</span>
            </div>
            <div className="divide-y divide-outline-variant">
              <div className="p-unit-md flex items-center space-x-unit-md hover:bg-surface-container-low transition-colors cursor-pointer">
                <div className="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[20px]">directions_boat</span>
                </div>
                <div className="flex-1">
                  <div className="text-[12px] font-semibold text-on-surface">Ever Given - Docking</div>
                  <div className="text-[10px] text-on-surface-variant font-medium">Terminal 4, Busan · ETA 14:30</div>
                </div>
                <div className="text-right">
                  <div className="text-[11px] text-emerald-600 font-bold">On Schedule</div>
                  <div className="text-[9px] text-on-surface-variant font-medium">SHP-2024-1547</div>
                </div>
              </div>
              <div className="p-unit-md flex items-center space-x-unit-md hover:bg-surface-container-low transition-colors cursor-pointer">
                <div className="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-amber-600">
                  <span className="material-symbols-outlined text-[20px]">local_shipping</span>
                </div>
                <div className="flex-1">
                  <div className="text-[12px] font-semibold text-on-surface">Truck Carrier #402</div>
                  <div className="text-[10px] text-on-surface-variant font-medium">Inland Hub, Berlin · ETA 18:00</div>
                </div>
                <div className="text-right">
                  <div className="text-[11px] text-amber-600 font-bold">Delayed 2h</div>
                  <div className="text-[9px] text-on-surface-variant font-medium">SHP-2024-1589</div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="card-surface rounded-xl overflow-hidden flex flex-col">
            <div className="p-unit-md border-b border-outline-variant flex justify-between items-center bg-surface-container-low rounded-t-xl">
              <h2 className="text-sm font-semibold text-on-surface">Risk Resolution Trends</h2>
              <select className="bg-transparent border-none text-[10px] text-on-surface-variant font-bold uppercase p-0 focus:ring-0 cursor-pointer outline-none">
                <option>Last 7 Days</option>
                <option>Last 30 Days</option>
              </select>
            </div>
            <div className="p-unit-md h-full flex flex-col items-center justify-center space-y-4">
              <div className="w-full flex items-end justify-between px-unit-md h-24 mb-4">
                <div className="w-8 bg-primary/20 rounded-t h-[60%]"></div>
                <div className="w-8 bg-primary/30 rounded-t h-[45%]"></div>
                <div className="w-8 bg-primary/40 rounded-t h-[75%]"></div>
                <div className="w-8 bg-primary/50 rounded-t h-[30%]"></div>
                <div className="w-8 bg-primary/60 rounded-t h-[85%]"></div>
                <div className="w-8 bg-primary rounded-t h-[95%] shadow-sm"></div>
              </div>
              <div className="text-center">
                <div className="text-[11px] text-on-surface-variant font-medium">AI Resolution Efficiency</div>
                <div className="text-lg font-bold text-emerald-600">88.4% Accuracy</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel: Agent Activity */}
      <div className="w-80 h-full overflow-hidden flex flex-col space-y-unit-lg">
        <div className="card-surface rounded-xl flex-1 flex flex-col">
          <div className="p-unit-md border-b border-outline-variant bg-surface-container-low flex items-center justify-between rounded-t-xl">
            <div className="flex items-center space-x-2">
              <span className="material-symbols-outlined text-primary text-[20px]">smart_toy</span>
              <h2 className="text-sm font-semibold text-on-surface">Agent Workflow</h2>
            </div>
            <span className="text-[9px] bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded font-bold uppercase">Active</span>
          </div>
          <div className="p-unit-md relative flex-1 overflow-y-auto">
            <div className="timeline-line"></div>
            <div className="space-y-6 relative z-10">
              
              {/* Step 1 */}
              <div className="flex items-start">
                <div className="w-6 h-6 rounded-full bg-emerald-100 border border-emerald-500 flex items-center justify-center mr-3 shrink-0">
                  <span className="material-symbols-outlined text-emerald-600 text-[14px] font-bold">check</span>
                </div>
                <div>
                  <div className="text-[11px] font-bold text-on-surface">Monitor Surveillance</div>
                  <div className="text-[10px] text-on-surface-variant mt-0.5 leading-relaxed font-medium">Scanning global weather & port AIS feeds. 1,420 nodes active.</div>
                </div>
              </div>
              
              {/* Step 2 */}
              <div className="flex items-start">
                <div className="w-6 h-6 rounded-full bg-emerald-100 border border-emerald-500 flex items-center justify-center mr-3 shrink-0">
                  <span className="material-symbols-outlined text-emerald-600 text-[14px] font-bold">check</span>
                </div>
                <div>
                  <div className="text-[11px] font-bold text-on-surface">Identify Exposure</div>
                  <div className="text-[10px] text-on-surface-variant mt-0.5 leading-relaxed font-medium">Shanghai Terminal 2 disruption mapped to 8 active POs.</div>
                </div>
              </div>
              
              {/* Step 3 */}
              <div className="flex items-start">
                <div className="w-6 h-6 rounded-full bg-emerald-100 border border-emerald-500 flex items-center justify-center mr-3 shrink-0">
                  <span className="material-symbols-outlined text-emerald-600 text-[14px] font-bold">check</span>
                </div>
                <div>
                  <div className="text-[11px] font-bold text-on-surface">Generate Alternatives</div>
                  <div className="text-[10px] text-on-surface-variant mt-0.5 leading-relaxed font-medium">3 reroute scenarios found via Ningbo Port.</div>
                </div>
              </div>
              
              {/* Step 4 (Current) */}
              <div className="flex items-start">
                <div className="w-6 h-6 rounded-full border border-amber-500 flex items-center justify-center mr-3 shrink-0 bg-white relative">
                  <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
                  <div className="absolute inset-0 rounded-full border border-amber-500 animate-ping opacity-20"></div>
                </div>
                <div>
                  <div className="text-[11px] font-bold text-amber-600">Reasoning Trade-offs</div>
                  <div className="text-[10px] text-amber-600/80 mt-0.5 leading-relaxed italic font-medium">Analyzing: Cost +$12k vs. Delay -3 days...</div>
                </div>
              </div>
              
              {/* Step 5 (Pending) */}
              <div className="flex items-start opacity-40">
                <div className="w-6 h-6 rounded-full border border-outline-variant flex items-center justify-center mr-3 shrink-0 bg-white">
                  <span className="w-1.5 h-1.5 rounded-full bg-outline-variant"></span>
                </div>
                <div>
                  <div className="text-[11px] font-bold text-on-surface-variant">Propose & Confirm</div>
                  <div className="text-[10px] text-on-surface-variant/70 mt-0.5 font-medium">Awaiting human oversight</div>
                </div>
              </div>

            </div>
          </div>
          <div className="p-unit-md bg-surface-container-low border-t border-outline-variant rounded-b-xl">
            <button className="w-full bg-primary text-white py-2 rounded-lg text-xs font-bold hover:brightness-110 transition-all flex items-center justify-center space-x-2 shadow-sm">
              <span>Approve Current Solution</span>
              <span className="material-symbols-outlined text-[16px]">chevron_right</span>
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
