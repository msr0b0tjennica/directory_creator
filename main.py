import subprocess
import time
import webbrowser
from pathlib import Path
import os
import sys
from typing import Dict, List
import uvicorn
from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
import threading

# Configuration for each service
SERVICES = {
    "user_service": {
        "path": "User Service code SVH",
        "port": 8000,
        "name": "User Service",
        "api_docs": "/docs"
    },
    "record_service": {
        "path": "Record Service code SVH",
        "port": 8001,
        "name": "Record Service",
        "api_docs": "/docs"
    },
    "ai_ml_service": {
        "path": "AI-ML Service code SVH",
        "port": 8002,
        "name": "AI/ML Service",
        "api_docs": "/docs"
    },
    "doctor_service": {
        "path": "Doctor Service code SVH",
        "port": 8003,
        "name": "Doctor Service",
        "api_docs": "/docs"
    },
    "telemedicine_service": {
        "path": "Telemedicine Service code SVH",
        "port": 8004,
        "name": "Telemedicine Service",
        "api_docs": "/docs"
    },
    "notification_service": {
        "path": "Notification Service code SVH",
        "port": 8005,
        "name": "Notification Service",
        "api_docs": "/docs"
    },
    "insurance_service": {
        "path": "Insurance Service code SVH",
        "port": 8006,
        "name": "Insurance Service",
        "api_docs": "/docs"
    }
}

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.base_dir = Path(__file__).parent.absolute()
        
    def start_service(self, service_name: str):
        """Start a specific service"""
        if service_name not in SERVICES:
            raise ValueError(f"Unknown service: {service_name}")
            
        service = SERVICES[service_name]
        service_path = self.base_dir / service["path"]
        port = service["port"]
        
        if service_name in self.processes:
            print(f"{service['name']} is already running on port {port}")
            return
            
        try:
            # Start the service in a new process
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "run:app", 
                "--host", "0.0.0.0", 
                "--port", str(port),
                "--reload"
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=str(service_path),
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.processes[service_name] = process
            print(f"Started {service['name']} on port {port}")
            
            # Open API docs in browser after a short delay
            threading.Timer(2, lambda: webbrowser.open_new_tab(
                f"http://localhost:{port}{service['api_docs']}"
            )).start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start {service['name']}: {str(e)}")
            return False
    
    def stop_service(self, service_name: str):
        """Stop a specific service"""
        if service_name in self.processes:
            self.processes[service_name].terminate()
            del self.processes[service_name]
            print(f"Stopped {SERVICES[service_name]['name']}")
            return True
        return False
    
    def stop_all_services(self):
        """Stop all running services"""
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
    
    def get_service_status(self, service_name: str) -> dict:
        """Check if a service is running and responding"""
        if service_name not in SERVICES:
            return {"status": "error", "message": "Unknown service"}
            
        service = SERVICES[service_name]
        url = f"http://localhost:{service['port']}/health"
        
        try:
            response = requests.get(url, timeout=2)
            return {
                "status": "running" if response.status_code == 200 else "error",
                "port": service["port"],
                "name": service["name"]
            }
        except:
            return {
                "status": "stopped",
                "port": service["port"],
                "name": service["name"]
            }

# Create FastAPI app for the management interface
app = FastAPI(title="SVH Service Manager")
manager = ServiceManager()

class ServiceStatus(BaseModel):
    name: str
    status: str
    port: int

@app.get("/")
async def root():
    """Root endpoint with service status"""
    status = []
    for service_name in SERVICES:
        status.append(manager.get_service_status(service_name))
    return {"services": status}

@app.post("/start/{service_name}")
async def start_service(service_name: str):
    """Start a specific service"""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
        
    success = manager.start_service(service_name)
    if success:
        return {"status": "starting", "service": service_name}
    else:
        raise HTTPException(status_code=500, detail="Failed to start service")

@app.post("/stop/{service_name}")
async def stop_service(service_name: str):
    """Stop a specific service"""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
        
    success = manager.stop_service(service_name)
    if success:
        return {"status": "stopped", "service": service_name}
    else:
        raise HTTPException(status_code=500, detail="Service was not running")

@app.get("/status")
async def get_status():
    """Get status of all services"""
    status = []
    for service_name in SERVICES:
        status.append(manager.get_service_status(service_name))
    return {"services": status}

def run_management_interface():
    """Run the management interface"""
    print("\n" + "="*50)
    print("Smart Health Vault - Service Manager")
    print("="*50)
    print("\nAvailable services:")
    for i, (service_name, service) in enumerate(SERVICES.items(), 1):
        print(f"{i}. {service['name']} (Port: {service['port']})")
    
    print("\nManagement interface running at http://localhost:8007")
    print("Press Ctrl+C to stop all services and exit\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8007)

if __name__ == "__main__":
    import atexit
    
    # Ensure all services are stopped when the manager exits
    atexit.register(manager.stop_all_services)
    
    try:
        # Start the management interface
        run_management_interface()
    except KeyboardInterrupt:
        print("\nStopping all services...")
        manager.stop_all_services()
        print("All services stopped. Exiting...")
        sys.exit(0)