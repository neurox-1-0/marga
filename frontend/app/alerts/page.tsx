import Link from "next/link";

export default function AlertsPage() {
  return (
    <main className="ml-64 mt-16 p-unit-lg h-[calc(100vh-64px)] overflow-y-auto space-y-unit-lg">
      
      {/* Header bar */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <h1 className="font-headline-lg text-on-surface">Active Alerts</h1>
          <span className="text-on-surface-variant">/</span>
          <span className="text-on-surface-variant text-sm font-medium">Live Disruptions</span>
        </div>
        <div className="flex items-center space-x-2 bg-surface-container-lowest border border-outline-variant px-3 py-1.5 rounded-full shadow-sm">
          <span className="text-error text-[10px]">●</span>
          <span className="text-on-surface font-medium text-xs">Live Status</span>
        </div>
      </div>

      {/* Filter Row */}
      <div className="flex justify-between items-center bg-surface-container-lowest p-2 rounded-lg border border-outline-variant shadow-sm">
        <div className="flex space-x-2">
          <button className="px-4 py-1.5 rounded-full bg-primary/10 text-primary font-bold text-xs uppercase tracking-widest">
            All
          </button>
          <button className="px-4 py-1.5 rounded-full bg-transparent text-on-surface-variant hover:bg-surface-container-high transition-colors font-bold text-xs uppercase tracking-widest">
            Awaiting Approval
          </button>
          <button className="px-4 py-1.5 rounded-full bg-transparent text-on-surface-variant hover:bg-surface-container-high transition-colors font-bold text-xs uppercase tracking-widest">
            In Progress
          </button>
          <button className="px-4 py-1.5 rounded-full bg-transparent text-on-surface-variant hover:bg-surface-container-high transition-colors font-bold text-xs uppercase tracking-widest">
            Monitoring
          </button>
        </div>
        
        <div className="relative w-64">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">search</span>
          <input
            type="text"
            placeholder="Search disruptions..."
            className="w-full bg-surface-container-low border border-outline-variant rounded-lg py-1.5 pl-10 pr-4 text-xs text-on-surface focus:outline-none focus:border-primary transition-all placeholder:text-on-surface-variant"
          />
        </div>
      </div>

      {/* Alert Cards */}
      <div className="space-y-4">
        {/* Card 1 */}
        <Link href="/alerts/1" className="block card-surface rounded-xl border-l-4 border-l-amber-500 p-unit-md hover:shadow-md transition-shadow cursor-pointer">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-[12px] font-semibold text-on-surface">Port Strike — Shanghai Terminal 2</h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest bg-error/10 text-error">
              High
            </span>
          </div>
          
          <div className="flex items-center space-x-3 mb-4">
            <p className="text-[10px] text-on-surface-variant font-medium flex items-center">
              Shanghai <span className="material-symbols-outlined text-[12px] mx-1">arrow_forward</span> Los Angeles
            </p>
            <span className="px-2 py-0.5 rounded bg-surface-container-high text-primary text-[10px] font-bold">
              8 POs Affected
            </span>
            <span className="px-2 py-0.5 rounded bg-error/10 text-error text-[10px] font-bold">
              $184,000 at risk
            </span>
          </div>

          <div className="h-1.5 bg-surface-container-low rounded-full overflow-hidden mb-3">
            <div className="h-full bg-amber-500 w-[78%]"></div>
          </div>
          
          <div className="flex justify-between items-center text-[9px] text-on-surface-variant font-bold uppercase tracking-widest">
            <span>Detected 23 min ago · Awaiting Approval</span>
            <span className="material-symbols-outlined text-primary text-[16px]">chevron_right</span>
          </div>
        </Link>

        {/* Card 2 */}
        <Link href="/alerts/2" className="block card-surface rounded-xl border-l-4 border-l-amber-500 p-unit-md hover:shadow-md transition-shadow cursor-pointer">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-[12px] font-semibold text-on-surface">Typhoon Mawar — South China Sea</h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest bg-error/10 text-error">
              High
            </span>
          </div>
          
          <div className="flex items-center space-x-3 mb-4">
            <p className="text-[10px] text-on-surface-variant font-medium flex items-center">
              Kaohsiung <span className="material-symbols-outlined text-[12px] mx-1">arrow_forward</span> Long Beach
            </p>
            <span className="px-2 py-0.5 rounded bg-surface-container-high text-primary text-[10px] font-bold">
              3 POs Affected
            </span>
            <span className="px-2 py-0.5 rounded bg-error/10 text-error text-[10px] font-bold">
              $62,000 at risk
            </span>
          </div>

          <div className="h-1.5 bg-surface-container-low rounded-full overflow-hidden mb-3">
            <div className="h-full bg-amber-500 w-[58%]"></div>
          </div>
          
          <div className="flex justify-between items-center text-[9px] text-on-surface-variant font-bold uppercase tracking-widest">
            <span>Detected 1 hr ago · Identifying Exposure</span>
            <span className="material-symbols-outlined text-primary text-[16px]">chevron_right</span>
          </div>
        </Link>

        {/* Card 3 */}
        <Link href="/alerts/3" className="block card-surface rounded-xl border-l-4 border-l-primary p-unit-md hover:shadow-md transition-shadow cursor-pointer">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-[12px] font-semibold text-on-surface">Suez Canal Delay — MV Nordic</h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest bg-surface-container-high text-on-surface-variant">
              Medium
            </span>
          </div>
          
          <div className="flex items-center space-x-3 mb-4">
            <p className="text-[10px] text-on-surface-variant font-medium flex items-center">
              Rotterdam <span className="material-symbols-outlined text-[12px] mx-1">arrow_forward</span> Singapore
            </p>
            <span className="px-2 py-0.5 rounded bg-surface-container-high text-primary text-[10px] font-bold">
              1 PO Affected
            </span>
            <span className="px-2 py-0.5 rounded bg-surface-container-high text-on-surface-variant text-[10px] font-bold">
              $38,000 at risk
            </span>
          </div>

          <div className="h-1.5 bg-surface-container-low rounded-full overflow-hidden mb-3">
            <div className="h-full bg-primary w-[36%]"></div>
          </div>
          
          <div className="flex justify-between items-center text-[9px] text-on-surface-variant font-bold uppercase tracking-widest">
            <span>Detected 3 hrs ago · Monitoring</span>
            <span className="material-symbols-outlined text-outline text-[16px]">chevron_right</span>
          </div>
        </Link>
      </div>

      <div className="pt-2 pb-6 flex justify-center">
        <p className="text-[10px] text-on-surface-variant font-bold uppercase tracking-widest">
          Showing 3 active disruptions · Total exposure: $284,000 · Last updated: just now
        </p>
      </div>
    </main>
  );
}
