const BASE_URL =
  import.meta.env.VITE_API_URL ||
  'https://icu-ai-monitor-d6z0.onrender.com';

const WS_URL =
  import.meta.env.VITE_WS_URL ||
  'wss://icu-ai-monitor-d6z0.onrender.com';

export const API = {
  async getSummary() {
    const res = await fetch(`${BASE_URL}/api/summary`);

    if (!res.ok) {
      throw new Error('Failed to fetch summary');
    }

    return res.json();
  },

  async getVitals() {
    const res = await fetch(`${BASE_URL}/api/vitals`);

    if (!res.ok) {
      throw new Error('Failed to fetch vitals');
    }

    return res.json();
  },

  createWebSocket(onMessage, onError) {
    const ws = new WebSocket(`${WS_URL}/stream`);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (e) {
        console.error('WS parse error:', e);
      }
    };

    ws.onerror = (e) => {
      console.error('WebSocket error:', e);

      if (onError) {
        onError(e);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };

    return ws;
  },
};
