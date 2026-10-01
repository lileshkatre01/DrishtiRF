import os
import sys
import time
import socket
import threading
import urllib.request
import uvicorn
import webview

from backend.core.utils import resource_path

def find_free_port() -> int:
    """Find a free TCP port automatically on localhost"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def run_server(port: int):
    """Run uvicorn server serving FastAPI app and frontend static files"""
    from backend.main import app
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    dist_dir = resource_path(os.path.join("frontend", "dist"))
    
    # Mount static frontend files if built frontend dist directory exists
    if os.path.exists(dist_dir):
        assets_dir = os.path.join(dist_dir, "assets")
        if os.path.exists(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        
        @app.get("/{catchall:path}")
        async def serve_spa(catchall: str):
            if catchall.startswith("api/") or catchall == "api" or catchall.startswith("ws"):
                return None
            file_path = os.path.join(dist_dir, catchall)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(dist_dir, "index.html"))

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

def main():
    port = find_free_port()
    
    # Start FastAPI/Uvicorn backend in background thread
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    # Wait until backend health endpoint responds
    health_url = f"http://127.0.0.1:{port}/api/health"
    for _ in range(60):
        try:
            with urllib.request.urlopen(health_url, timeout=1) as resp:
                if resp.status == 200:
                    break
        except Exception:
            time.sleep(0.1)

    app_url = f"http://127.0.0.1:{port}"

    # Open PyWebView Desktop Window
    window = webview.create_window(
        title="DrishtiRF — SIGINT Analysis Platform",
        url=app_url,
        width=1400,
        height=900,
        min_size=(1024, 700),
        resizable=True
    )
    
    # Start webview GUI event loop
    webview.start()
    
    # When window closes, exit app completely and stop uvicorn backend
    sys.exit(0)

if __name__ == "__main__":
    main()
