"use client";
import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { connectAgentStream } from "../../lib/api";

const RouteMap = dynamic(
  () => import("../../components/RouteMap").then((m) => ({ default: m.RouteMap })),
  { ssr: false, loading: () => <div className="h-full bg-[#0b1329] rounded-xl flex items-center justify-center text-slate-500 text-xs animate-pulse">Loading map…</div> }
);

export default function MapPage() {
  const [activeStep, setActiveStep] = useState(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("agentActiveStep");
      if (saved) return parseInt(saved, 10);
    }
    return 1;
  });

  useEffect(() => {
    localStorage.setItem("agentActiveStep", activeStep.toString());
  }, [activeStep]);

  useEffect(() => {
    const disconnect = connectAgentStream((data) => {
      const thought = data?.data?.thought?.toLowerCase() || "";
      const node = data?.data?.node || "";

      if (node === "execute" && thought.includes("rejected")) setActiveStep(7);
      else if (node === "execute" || thought.includes("executing")) setActiveStep(6);
      else if (node === "hitl_gate" || thought.includes("hitl") || thought.includes("pending")) setActiveStep(5);
      else if (thought.includes("cost") || thought.includes("stockout") || thought.includes("saving")) setActiveStep(4);
      else if (thought.includes("freight") || thought.includes("quote")) setActiveStep(3);
      else if (thought.includes("exposure") || thought.includes("erp") || thought.includes("po")) setActiveStep(2);
    });
    return () => disconnect();
  }, []);

  return (
    <main className="ml-64 mt-16 p-unit-lg h-[calc(100vh-64px)] overflow-hidden flex flex-col space-y-unit-md">
      <div className="flex justify-between items-center shrink-0">
        <h1 className="font-headline-lg text-on-surface">Global Route Map</h1>
        <span className="flex items-center text-[10px] text-emerald-600 bg-emerald-50 border border-emerald-200 px-2 py-1 rounded-lg font-bold">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse mr-1.5"></span>
          Live Telemetry Active
        </span>
      </div>
      
      <div className="flex-1 min-h-0">
        <RouteMap activeStep={activeStep} />
      </div>
    </main>
  );
}
