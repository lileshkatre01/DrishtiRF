"""
DrishtiRF - WebSocket Real-Time Progress & Signal Streaming Router
Provides WebSocket connections for live waterfall streaming, stage progress updates, and notifications.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
import json
import asyncio

from backend.core.logging import logger

class ConnectionManager:
    def __init__(self):
        # Map job_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)
        logger.info(f"WebSocket client connected to job_id: {job_id}")

    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            if websocket in self.active_connections[job_id]:
                self.active_connections[job_id].remove(websocket)
            if len(self.active_connections[job_id]) == 0:
                del self.active_connections[job_id]
        logger.info(f"WebSocket client disconnected from job_id: {job_id}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_job(self, job_id: str, message: Dict[str, Any]):
        if job_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send WS message: {str(e)}")
                    disconnected.append(connection)
            for conn in disconnected:
                self.disconnect(conn, job_id)

manager = ConnectionManager()
router = APIRouter(tags=["Real-Time Streaming"])

@router.websocket("/ws/jobs/{job_id}")
async def websocket_job_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates, stage results, and signal stream chunks.
    """
    await manager.connect(websocket, job_id)
    try:
        # Send initial acknowledgement
        await manager.send_personal_message({
            "type": "CONNECTION_ESTABLISHED",
            "job_id": job_id,
            "message": f"Connected to real-time telemetry stream for job {job_id}"
        }, websocket)

        while True:
            try:
                data = await websocket.receive_text()
                if not data:
                    break
                payload = json.loads(data)
                if payload.get("action") == "ping":
                    await manager.send_personal_message({"type": "pong", "job_id": job_id}, websocket)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.debug(f"WS receive loop iteration for job {job_id}: {str(e)}")
                break

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, job_id)

def notify_job_progress(job_id: str, stage: str, progress: float, status: str, payload: Optional[Dict[str, Any]] = None):
    """
    Helper function to broadcast job progress updates synchronously or asynchronously.
    """
    msg = {
        "type": "STAGE_PROGRESS",
        "job_id": job_id,
        "stage": stage,
        "progress": float(progress),
        "status": status,
        "payload": payload or {}
    }
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast_to_job(job_id, msg))
        else:
            loop.run_until_complete(manager.broadcast_to_job(job_id, msg))
    except Exception:
        # Fallback if no running loop in synchronous thread
        pass
