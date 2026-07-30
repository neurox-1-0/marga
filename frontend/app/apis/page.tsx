import Link from "next/link";

export default function APIsPage() {
  const apis = [
    {
      name: "Marga Agent Backend",
      port: 8004,
      description: "The core LangGraph supply chain AI agent that orchestrates reasoning, NOAA polling, and HITL decision-making.",
      icon: "robot_2",
      docsUrl: "http://localhost:8004/docs"
    },
    {
      name: "Mock ERP System",
      port: 8001,
      description: "Simulates an enterprise resource planning system holding active Purchase Orders, inventory values, and supplier details.",
      icon: "database",
      docsUrl: "http://localhost:8001/docs"
    },
    {
      name: "Mock Freight Carrier",
      port: 8002,
      description: "Provides dynamic multimodal freight quotes modeled after project44 APIs, including OAuth flows and live rate calculation.",
      icon: "local_shipping",
      docsUrl: "http://localhost:8002/docs"
    },
    {
      name: "Mock Booking Engine",
      port: 8003,
      description: "Handles final execution of rerouted shipments, generating booking references and completing the agent's workflow.",
      icon: "task_alt",
      docsUrl: "http://localhost:8003/docs"
    }
  ];

  return (
    <main className="ml-64 mt-16 p-unit-lg max-w-5xl">
      <div className="mb-8">
        <h1 className="font-headline-lg text-on-surface mb-2">API Integrations</h1>
        <p className="text-on-surface-variant font-medium">
          Marga operates across a microservice architecture. Explore the Swagger/OpenAPI documentation for each connected service below.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-unit-md">
        {apis.map((api) => (
          <div key={api.name} className="card-surface p-unit-md rounded-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-primary">{api.icon}</span>
                </div>
                <div>
                  <h2 className="text-on-surface font-bold text-lg">{api.name}</h2>
                  <p className="text-on-surface-variant text-xs font-mono">Port: {api.port}</p>
                </div>
              </div>
              <p className="text-on-surface-variant text-sm font-medium leading-relaxed mb-6">
                {api.description}
              </p>
            </div>
            <a 
              href={api.docsUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              className="w-full bg-surface-container-low hover:bg-primary hover:text-white transition-colors text-primary border border-outline-variant rounded-lg py-3 font-semibold flex items-center justify-center text-sm"
            >
              <span className="material-symbols-outlined text-[18px] mr-2">open_in_new</span> 
              View Swagger Docs
            </a>
          </div>
        ))}
      </div>
    </main>
  );
}
