import { useState, useEffect, useRef } from 'react';

export function useVitalsStream(wsUrl, initialHistory = []) {
  const [data, setData] = useState(initialHistory);
  const [isConnected, setIsConnected] = useState(false);
  const [latestVital, setLatestVital] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    setData(initialHistory);
  }, [initialHistory]);

  useEffect(() => {
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);

    ws.current.onmessage = (event) => {
      const newVital = JSON.parse(event.data);
      setLatestVital(newVital);
      setData((prev) => {
        const newData = [...prev, newVital];
        if (newData.length > 1500) {
          newData.shift(); // Keep array size manageable for real-time visualization (45 mins + buffer)
        }
        return newData;
      });
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, [wsUrl]);

  return { data, isConnected, latestVital };
}
