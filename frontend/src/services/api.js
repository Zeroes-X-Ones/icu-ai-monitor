const BASE_URL = 'https://icu-ai-monitor-d6z0.onrender.com';

const WS_URL = 'wss://icu-ai-monitor-d6z0.onrender.com';

export const API = {
  async getSummary(window = 15) {
    const res = await fetch(
      `${BASE_URL}/api/v1/analysis/?window=${window}`
    );

    if (!res.ok) {
      throw new Error('Failed to fetch analysis');
    }

    return res.json();
  },

  async getVitals() {
    const res = await fetch(
      `${BASE_URL}/api/v1/vitals/latest`
    );

    if (!res.ok) {
      throw new Error('Failed to fetch vitals');
    }

    return res.json();
  },

  async getHistory(minutes = 60) {
    const res = await fetch(
      `${BASE_URL}/api/v1/vitals/history?minutes=${minutes}`
    );

    if (!res.ok) {
      throw new Error('Failed to fetch history');
    }

    return res.json();
  },

  async getAlerts(limit = 5) {
    const res = await fetch(
      `${BASE_URL}/api/v1/vitals/alerts?limit=${limit}`
    );

    if (!res.ok) {
      throw new Error('Failed to fetch alerts');
    }

    return res.json();
  },

  createWebSocket(onMessage, onError) {
    const ws = new WebSocket(
      `${WS_URL}/api/v1/ws/stream`
    );

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
