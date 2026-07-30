"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface ApiCallEvent {
  service: string;
  endpoint: string;
  request: any;
  response: any;
  status: number;
}

export default function APIsPage() {
  const [liveCalls, setLiveCalls] = useState<Record<string, ApiCallEvent>>({});

  useEffect(() => {
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8004/ws/dashboard";
    const ws = new WebSocket(WS_URL);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "api_call") {
          setLiveCalls((prev) => ({
            ...prev,
            [data.data.service]: data.data,
          }));
        }
      } catch (e) {
        console.error("Error parsing WS message:", e);
      }
    };

    return () => {
      ws.close();
    };
  }, []);

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
        <h1 className="font-headline-lg text-on-surface mb-2">API Integrations & Live Monitor</h1>
        <p className="text-on-surface-variant font-medium">
          Marga operates across a microservice architecture. Below you can view the Swagger docs and monitor real-time API payloads when the agent is running a workflow.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-unit-md">
        {apis.map((api) => {
          const latestCall = liveCalls[api.name];
          
          return (
            <div key={api.name} className="card-surface p-unit-md rounded-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-primary">{api.icon}</span>
                    </div>
                    <div>
                      <h2 className="text-on-surface font-bold text-lg">{api.name}</h2>
                      <p className="text-on-surface-variant text-xs font-mono">Port: {api.port}</p>
                    </div>
                  </div>
                  <a 
                    href={api.docsUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="bg-surface-container-low hover:bg-primary hover:text-white transition-colors text-primary border border-outline-variant rounded-lg px-4 py-2 font-semibold flex items-center text-sm"
                  >
                    <span className="material-symbols-outlined text-[18px] mr-2">open_in_new</span> 
                    Swagger Docs
                  </a>
                </div>
                <p className="text-on-surface-variant text-sm font-medium leading-relaxed mb-6">
                  {api.description}
                </p>

                {/* Live Call Monitor */}
                <div className="mt-4 bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden">
                  <div className="bg-surface-container-low px-4 py-2 border-b border-outline-variant flex items-center justify-between">
                    <span className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Live API Traffic Monitor</span>
                    {latestCall ? (
                      <span className="flex items-center text-xs font-bold text-green-500">
                        <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
                        {latestCall.status} OK • {latestCall.endpoint}
                      </span>
                    ) : (
                      <span className="flex items-center text-xs font-medium text-on-surface-variant">
                        Waiting for traffic...
                      </span>
                    )}
                  </div>
                  
                  {latestCall && (
                    <div className="grid grid-cols-2 divide-x divide-outline-variant max-h-64 overflow-y-auto font-mono text-[10px]">
                      <div className="p-3">
                        <div className="text-primary font-bold mb-2">REQUEST PAYLOAD</div>
                        <pre className="text-on-surface whitespace-pre-wrap">
                          {JSON.stringify(latestCall.request, null, 2)}
                        </pre>
                      </div>
                      <div className="p-3">
                        <div className="text-primary font-bold mb-2">RESPONSE PAYLOAD</div>
                        <pre className="text-on-surface whitespace-pre-wrap">
                          {JSON.stringify(latestCall.response, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </main>
  );
}
