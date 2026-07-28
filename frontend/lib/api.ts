export interface EventSchema {
  event_id: string;
  detected_at: string;
  source: string;
  vessel_id: string;
  route: string;
  description: string;
}

export interface ExposureSchema {
  matched_pos: string[];
  total_inventory_value_usd: number;
}

export interface FreightQuoteSchema {
  quote_id: string;
  carrier: string;
  mode: string;
  cost_usd: number;
  transit_days: number;
}

export interface CostAnalysisSchema {
  stockout_cost_usd: number;
  reroute_savings_usd: number;
  recommendation: string;
  best_reroute_option?: { quote_id: string } | null;
}

export interface FreightOptionsSchema {
  quotes: FreightQuoteSchema[];
}

export interface ApprovalCard {
  event: EventSchema;
  exposure: ExposureSchema;
  cost_analysis: CostAnalysisSchema;
  freight_options: FreightOptionsSchema;
  status: string;
  chosen_quote_id?: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/dashboard";

export async function getPendingCards(): Promise<ApprovalCard[]> {
  const response = await fetch(`${API_BASE}/cards/pending`, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error('Failed to fetch pending cards');
  }
  return response.json();
}

export async function submitDecision(
  eventId: string,
  decision: 'approved' | 'rejected' | 'redirected',
  chosenQuoteId: string | null,
  managerNote: string
): Promise<{ status: string; decision: string }> {
  const response = await fetch(`${API_BASE}/cards/${eventId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event_id: eventId,
      decision: decision,
      chosen_quote_id: chosenQuoteId,
      manager_note: managerNote
    })
  });
  if (!response.ok) {
    throw new Error('Failed to submit decision');
  }
  return response.json();
}

export async function triggerDemoDisruption(eventId: string): Promise<{ status: string; thread_id: string }> {
  const response = await fetch(`${API_BASE}/trigger_disruption?event_id=${eventId}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to trigger disruption');
  }
  return response.json();
}

export function connectAgentStream(onMessage: (data: any) => void): () => void {
  let ws: WebSocket | null = null;
  let isIntentionalClose = false;
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

  const connect = () => {
    console.log("Connecting WebSocket to:", WS_URL);
    ws = new WebSocket(WS_URL);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (e) {
        console.error("Failed to parse websocket message", e);
      }
    };
    
    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket closed.");
      if (!isIntentionalClose) {
        console.log("Reconnecting in 2 seconds...");
        reconnectTimeout = setTimeout(connect, 2000);
      }
    };
  };

  connect();
  
  return () => {
    isIntentionalClose = true;
    if (reconnectTimeout) clearTimeout(reconnectTimeout);
    if (ws) ws.close();
  };
}
