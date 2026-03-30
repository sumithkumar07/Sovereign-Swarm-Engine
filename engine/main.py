import os
import ctypes
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Sovereign Swarm Intelligence API")

# --- LOAD NATIVE C++ ENGINE ---
LIB_PATH = os.path.join(os.path.dirname(__file__), "libsovereign.so")

# Fallback for Windows local testing
if os.name == 'nt':
    LIB_PATH = os.path.join(os.path.dirname(__file__), "sovereign.dll")

class SovereignAPI:
    def __init__(self):
        try:
            self.lib = ctypes.CDLL(LIB_PATH)
            
            # Function signatures
            self.lib.sovereign_init_master.restype = ctypes.c_void_p
            
            self.lib.sovereign_init_agent.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int]
            self.lib.sovereign_init_agent.restype = ctypes.c_void_p
            
            self.lib.sovereign_agent_observe.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            
            self.lib.sovereign_agent_act.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]
            self.lib.sovereign_agent_act.restype = ctypes.c_char_p
            
            # Initialize Global Brain
            self.master_brain = self.lib.sovereign_init_master()
            
            # Initialize Agents
            self.agents = {
                "Alpha": self.lib.sovereign_init_agent(b"Titan-Alpha", self.master_brain, 101),
                "Beta": self.lib.sovereign_init_agent(b"Titan-Beta", self.master_brain, 202),
                "Delta": self.lib.sovereign_init_agent(b"Titan-Delta", self.master_brain, 303),
                "Gamma": self.lib.sovereign_init_agent(b"Titan-Gamma", self.master_brain, 404),
            }
            print("[SUCCESS] Sovereign Swarm Engine Loaded into RAM.")
        except Exception as e:
            print(f"[ERROR] Failed to load native engine: {e}")
            self.lib = None

# Global Engine Instance
engine = SovereignAPI()

class ObserveRequest(BaseModel):
    agent_id: str
    text: str

class ActRequest(BaseModel):
    agent_id: str
    max_chars: Optional[int] = 50
    temp: Optional[float] = 0.5

@app.get("/")
async def root():
    return {
        "status": "online",
        "platform": "Sovereign Swarm Intelligence",
        "engine": "v1.50 Titan-C++",
        "endpoint": "locallab.sbs"
    }

@app.get("/status")
async def get_status():
    return {
        "agents_ready": list(engine.agents.keys()) if engine.lib else [],
        "engine_loaded": engine.lib is not None
    }

@app.post("/observe")
async def observe(req: ObserveRequest):
    if not engine.lib or req.agent_id not in engine.agents:
        return {"error": "Engine not loaded or invalid agent"}
    
    agent_ptr = engine.agents[req.agent_id]
    engine.lib.sovereign_agent_observe(agent_ptr, req.text.encode('utf-8'))
    return {"status": f"{req.agent_id} observed event"}

@app.post("/act")
async def act(req: ActRequest):
    if not engine.lib or req.agent_id not in engine.agents:
        return {"error": "Engine not loaded or invalid agent"}
    
    agent_ptr = engine.agents[req.agent_id]
    response = engine.lib.sovereign_agent_act(agent_ptr, req.max_chars, req.temp)
    return {
        "agent": req.agent_id,
        "content": response.decode('utf-8'),
        "timestamp": "Synchronous"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860) # Default HF Space Port
