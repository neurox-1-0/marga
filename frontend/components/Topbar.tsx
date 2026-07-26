export default function Topbar() {
  return (
    <header className="bg-surface/80 backdrop-blur-md h-16 fixed top-0 right-0 left-64 border-b border-outline-variant flex items-center justify-between px-unit-xl z-40">
      <div className="flex items-center space-x-unit-sm">
        <span className="font-headline-md text-on-surface">Overview</span>
        <span className="text-on-surface-variant">/</span>
        <span className="text-on-surface-variant text-sm font-medium">Global Supply Chain</span>
      </div>
      <div className="flex items-center space-x-unit-lg">
        <div className="relative w-80">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">search</span>
          <input className="w-full bg-surface-container-low border border-outline-variant rounded-lg py-1.5 pl-10 pr-4 text-xs text-on-surface focus:outline-none focus:border-primary transition-all placeholder:text-on-surface-variant" placeholder="Search POs, shipments, routes..." type="text" />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 bg-surface-container-high px-1.5 py-0.5 rounded border border-outline-variant text-[10px] text-on-surface-variant">/</div>
        </div>
        <div className="flex items-center space-x-unit-md border-l border-outline-variant pl-unit-lg">
          <button className="text-on-surface-variant hover:text-primary transition-colors relative">
            <span className="material-symbols-outlined text-[22px]">notifications</span>
            <span className="absolute top-0 right-0 w-2 h-2 bg-error rounded-full ring-2 ring-surface"></span>
          </button>
          <div className="flex items-center space-x-unit-sm cursor-pointer hover:bg-surface-container-low p-1 rounded-lg transition-all">
            <div className="text-right hidden sm:block">
              <div className="text-xs font-semibold text-on-surface">Alex Rivera</div>
              <div className="text-[10px] text-on-surface-variant">Operations Lead</div>
            </div>
            <img alt="Profile" className="w-8 h-8 rounded-full border border-outline-variant" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDzXWKd2ns3opLkdkKMp6RGhUUCyBm7ryQTCzM3lpVyLQMux_ZgmiWfO8vV_-3lBFqiKMpo7p2lUqpnXAn4MOUFqmzQrW6mjwxT9PazYBlrDvQhW7mrU0AZ-ehBED0vemOchI0wRrE_wHXJxBfbx7YAg3kHZVadCsKTsmLlI-GfPJqM0ratr8MAu9rNBvGa9Edg-gBAVaIkET7_kqJiRAl_PGLRWW6y_yEvi92qqVByS7zIatPLZy9jbZmElxzrgnqvQI4ZcnW9QPk2" />
          </div>
        </div>
      </div>
    </header>
  );
}
