// src/services/realtime.ts
type WebSocketCallback = (data: any) => void;

class RealtimeService {
  private socket: WebSocket | null = null;
  private callbacks: Map<string, Set<WebSocketCallback>> = new Map();
  private isConnecting = false;
  private url: string = '';

  connect(auctionId?: string) {
    if (this.socket || this.isConnecting) return;

    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD
      ? 'https://bidzo-backend-fqzw.onrender.com/api'
      : 'http://localhost:8000/api');
    const backendUrl = new URL(apiBaseUrl);
    const protocol = backendUrl.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = backendUrl.host;

    this.url = auctionId ? `${protocol}//${host}/ws/auctions/${auctionId}/` : `${protocol}//${host}/ws/auctions/`;

    this.isConnecting = true;
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log(`[Realtime] Connected to ${this.url}`);
      this.isConnecting = false;
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const eventType = data.type;

        if (eventType && this.callbacks.has(eventType)) {
          this.callbacks.get(eventType)!.forEach(cb => cb(data));
        }
      } catch (err) {
        console.error('[Realtime] Message parse error:', err);
      }
    };

    this.socket.onclose = () => {
      console.log(`[Realtime] Disconnected from ${this.url}`);
      this.socket = null;
      this.isConnecting = false;
      // Simple reconnect logic
      setTimeout(() => this.connect(auctionId), 3000);
    };

    this.socket.onerror = (err) => {
      console.error(`[Realtime] WebSocket error:`, err);
    };
  }

  subscribe(eventType: string, callback: WebSocketCallback) {
    if (!this.callbacks.has(eventType)) {
      this.callbacks.set(eventType, new Set());
    }
    this.callbacks.get(eventType)!.add(callback);

    return () => this.unsubscribe(eventType, callback);
  }

  unsubscribe(eventType: string, callback: WebSocketCallback) {
    if (this.callbacks.has(eventType)) {
      this.callbacks.get(eventType)!.delete(callback);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.onclose = null; // Disable auto-reconnect
      this.socket.close();
      this.socket = null;
    }
    this.isConnecting = false;
    this.callbacks.clear();
  }
}

export const realtime = new RealtimeService();
