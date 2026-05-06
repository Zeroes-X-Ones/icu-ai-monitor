import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.vitals_generator import generate_vitals, get_history
from app.services.distress_detector import calculate_distress
from app.services.medical_summarizer import generate_summary

router = APIRouter()

# Track connected clients
active_connections: list[WebSocket] = []


@router.websocket("/stream")
async def vitals_stream(websocket: WebSocket):
    """Stream real-time vitals every 2 seconds to the connected client."""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            vitals = generate_vitals()
            distress = calculate_distress(
                vitals["heart_rate"],
                vitals["spo2"],
                vitals["respiratory_rate"],
            )
            history = get_history()
            summary_data = generate_summary(history, vitals)

            payload = {
                "vitals": vitals,
                "distress": distress,
                "trends": summary_data.get("trends", {}),
                "history": history[-30:],  # send last 30 points to keep payload light
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception:
        if websocket in active_connections:
            active_connections.remove(websocket)
