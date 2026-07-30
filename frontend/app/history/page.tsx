
export default function HistoryPage() {
  return (
    <main className="ml-64 mt-16 p-unit-lg h-[calc(100vh-64px)] overflow-y-auto space-y-unit-lg">
      
      {/* Header bar */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <h1 className="font-headline-lg text-on-surface">Risk History</h1>
          <span className="text-on-surface-variant">/</span>
          <span className="text-on-surface-variant text-sm font-medium">Resolution Ledger</span>
        </div>
      </div>

      {/* Stat Cards Row */}
      <div className="grid grid-cols-3 gap-unit-md">
        
        {/* Card 1 */}
        <div className="card-surface p-unit-md rounded-xl flex flex-col justify-between h-36">
          <div className="flex justify-between items-center text-on-surface-variant mb-4">
            <span className="text-[10px] font-bold uppercase tracking-widest">Total Disruptions Handled</span>
            <span className="material-symbols-outlined text-primary text-[18px]">history</span>
          </div>
          <div className="flex items-end justify-between">
            <div>
              <div className="text-2xl font-bold text-on-surface leading-none">47</div>
              <div className="text-[10px] text-primary mt-1 flex items-center">
                <span className="material-symbols-outlined text-[12px] mr-1">trending_up</span>
                +4 This Month
              </div>
            </div>
            <div className="flex items-end space-x-0.5 h-8">
              <div className="sparkline-bar bg-primary/20 h-2"></div>
              <div className="sparkline-bar bg-primary/30 h-4"></div>
              <div className="sparkline-bar bg-primary/50 h-5"></div>
              <div className="sparkline-bar bg-primary/70 h-7"></div>
              <div className="sparkline-bar bg-primary h-8"></div>
            </div>
          </div>
        </div>

        {/* Card 2 */}
        <div className="card-surface p-unit-md rounded-xl flex flex-col justify-between h-36">
          <div className="flex justify-between items-center text-on-surface-variant mb-4">
            <span className="text-[10px] font-bold uppercase tracking-widest">Avg Response Time</span>
            <span className="material-symbols-outlined text-amber-500 text-[18px]">timer</span>
          </div>
          <div className="flex items-end justify-between">
            <div>
              <div className="text-2xl font-bold text-on-surface leading-none">18 min</div>
              <div className="text-[10px] text-emerald-600 mt-1 flex items-center">
                <span className="material-symbols-outlined text-[12px] mr-1">trending_down</span>
                -2 min vs avg
              </div>
            </div>
            <div className="flex items-end space-x-0.5 h-8">
              <div className="sparkline-bar bg-amber-500/20 h-6"></div>
              <div className="sparkline-bar bg-amber-500/30 h-5"></div>
              <div className="sparkline-bar bg-amber-500/50 h-4"></div>
              <div className="sparkline-bar bg-amber-500/70 h-3"></div>
              <div className="sparkline-bar bg-amber-500 h-2"></div>
            </div>
          </div>
        </div>

        {/* Card 3 */}
        <div className="card-surface p-unit-md rounded-xl flex flex-col justify-between h-36">
          <div className="flex justify-between items-center text-on-surface-variant mb-4">
            <span className="text-[10px] font-bold uppercase tracking-widest">Cost Avoided (Est.)</span>
            <span className="material-symbols-outlined text-emerald-500 text-[18px]">savings</span>
          </div>
          <div className="flex items-end justify-between">
            <div>
              <div className="text-2xl font-bold text-on-surface leading-none">$1.2M</div>
              <div className="text-[10px] text-emerald-600 mt-1 flex items-center">
                <span className="material-symbols-outlined text-[12px] mr-1">trending_up</span>
                +15.2% YTD
              </div>
            </div>
            <div className="flex items-end space-x-0.5 h-8">
              <div className="sparkline-bar bg-emerald-500/20 h-3"></div>
              <div className="sparkline-bar bg-emerald-500/30 h-4"></div>
              <div className="sparkline-bar bg-emerald-500/50 h-6"></div>
              <div className="sparkline-bar bg-emerald-500/70 h-7"></div>
              <div className="sparkline-bar bg-emerald-500 h-8"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Row */}
      <div className="flex justify-between items-center">
        <button className="flex items-center space-x-2 border border-outline-variant text-on-surface-variant text-[11px] rounded-lg px-unit-md py-unit-sm hover:bg-surface-container-high transition-colors font-medium">
          <span>Past 30 days</span>
          <span className="material-symbols-outlined text-[14px]">expand_more</span>
        </button>
        <button className="flex items-center space-x-2 border border-outline-variant text-on-surface-variant text-[11px] rounded-lg px-unit-md py-unit-sm hover:bg-surface-container-high transition-colors font-medium">
          <span className="material-symbols-outlined text-[14px]">download</span>
          <span>Export</span>
        </button>
      </div>

      {/* History Table */}
      <div className="card-surface rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface-container-low border-b border-outline-variant text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                <th className="px-4 py-3">Event</th>
                <th className="px-4 py-3">Route</th>
                <th className="px-4 py-3">Risk</th>
                <th className="px-4 py-3">Decision</th>
                <th className="px-4 py-3">Reroute Cost</th>
                <th className="px-4 py-3">Cost Avoided</th>
                <th className="px-4 py-3">Response Time</th>
                <th className="px-4 py-3">Resolved</th>
                <th className="px-4 py-3 text-right"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant text-[11px]">
              
              {/* Row 1 */}
              <tr className="hover:bg-surface-container-low transition-colors group">
                <td className="px-4 py-3 font-semibold text-on-surface">Port Congestion — Busan</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">Busan <span className="mx-1">→</span> Seattle</td>
                <td className="px-4 py-3">
                  <span className="bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">Medium</span>
                </td>
                <td className="px-4 py-3">
                  <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">Approved</span>
                </td>
                <td className="px-4 py-3 text-on-surface font-mono font-medium">$3,200</td>
                <td className="px-4 py-3 text-emerald-600 font-mono font-medium">$19,000</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">12 min</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">3 days ago</td>
                <td className="px-4 py-3 text-right">
                  <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-[16px]">open_in_new</span>
                </td>
              </tr>

              {/* Row 2 */}
              <tr className="hover:bg-surface-container-low transition-colors group">
                <td className="px-4 py-3 font-semibold text-on-surface">Typhoon Khanun</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">Manila <span className="mx-1">→</span> Tokyo</td>
                <td className="px-4 py-3">
                  <span className="bg-error/10 text-error px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">High</span>
                </td>
                <td className="px-4 py-3">
                  <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">Approved</span>
                </td>
                <td className="px-4 py-3 text-on-surface font-mono font-medium">$6,800</td>
                <td className="px-4 py-3 text-emerald-600 font-mono font-medium">$54,000</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">8 min</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">5 days ago</td>
                <td className="px-4 py-3 text-right">
                  <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-[16px]">open_in_new</span>
                </td>
              </tr>

              {/* Row 3 */}
              <tr className="hover:bg-surface-container-low transition-colors group">
                <td className="px-4 py-3 font-semibold text-on-surface">Rail Strike — France</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">Paris <span className="mx-1">→</span> Lyon</td>
                <td className="px-4 py-3">
                  <span className="bg-surface-container-high text-on-surface-variant px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">Low</span>
                </td>
                <td className="px-4 py-3">
                  <span className="bg-error/10 text-error px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">Rejected</span>
                </td>
                <td className="px-4 py-3 text-on-surface-variant font-mono font-medium">—</td>
                <td className="px-4 py-3 text-on-surface-variant font-mono font-medium">—</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">31 min</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">1 week ago</td>
                <td className="px-4 py-3 text-right">
                  <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-[16px]">open_in_new</span>
                </td>
              </tr>

              {/* Row 4 */}
              <tr className="hover:bg-surface-container-low transition-colors group">
                <td className="px-4 py-3 font-semibold text-on-surface">Vessel Delay — MV Aurora</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">Hamburg <span className="mx-1">→</span> NYC</td>
                <td className="px-4 py-3">
                  <span className="bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">Medium</span>
                </td>
                <td className="px-4 py-3">
                  <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">Approved</span>
                </td>
                <td className="px-4 py-3 text-on-surface font-mono font-medium">$4,100</td>
                <td className="px-4 py-3 text-emerald-600 font-mono font-medium">$31,000</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">15 min</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">1 week ago</td>
                <td className="px-4 py-3 text-right">
                  <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-[16px]">open_in_new</span>
                </td>
              </tr>

              {/* Row 5 */}
              <tr className="hover:bg-surface-container-low transition-colors group">
                <td className="px-4 py-3 font-semibold text-on-surface">Port Strike — Felixstowe</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">London <span className="mx-1">→</span> Boston</td>
                <td className="px-4 py-3">
                  <span className="bg-error/10 text-error px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">High</span>
                </td>
                <td className="px-4 py-3">
                  <span className="bg-primary/10 text-primary px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">Redirected</span>
                </td>
                <td className="px-4 py-3 text-on-surface font-mono font-medium">$2,900</td>
                <td className="px-4 py-3 text-emerald-600 font-mono font-medium">$47,000</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">22 min</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">2 weeks ago</td>
                <td className="px-4 py-3 text-right">
                  <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-[16px]">open_in_new</span>
                </td>
              </tr>

              {/* Row 6 */}
              <tr className="hover:bg-surface-container-low transition-colors group">
                <td className="px-4 py-3 font-semibold text-on-surface">Customs Delay — Rotterdam</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">Rotterdam <span className="mx-1">→</span> Chicago</td>
                <td className="px-4 py-3">
                  <span className="bg-surface-container-high text-on-surface-variant px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">Low</span>
                </td>
                <td className="px-4 py-3">
                  <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold text-[9px] uppercase tracking-widest">Approved</span>
                </td>
                <td className="px-4 py-3 text-on-surface font-mono font-medium">$1,400</td>
                <td className="px-4 py-3 text-emerald-600 font-mono font-medium">$8,500</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">9 min</td>
                <td className="px-4 py-3 text-on-surface-variant font-medium">2 weeks ago</td>
                <td className="px-4 py-3 text-right">
                  <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer text-[16px]">open_in_new</span>
                </td>
              </tr>

            </tbody>
          </table>
        </div>
        
        <div className="bg-surface-container-low border-t border-outline-variant px-unit-md py-unit-sm">
          <p className="text-[10px] text-on-surface-variant font-medium text-center">
            Showing 6 of 47 records · All decisions are fully auditable · Every entry links to its original event log
          </p>
        </div>
      </div>
      
    </main>
  );
}
