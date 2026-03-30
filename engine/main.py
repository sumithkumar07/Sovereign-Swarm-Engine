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
        self.lib = None
        self.master_brain = None
        self.agents = {}
        
        try:
            if not os.path.exists(LIB_PATH):
                print(f"[ERROR] Binary not found at {LIB_PATH}")
                return

            self.lib = ctypes.CDLL(LIB_PATH)
            
            # --- STRICT FUNCTION SIGNATURES (64-BIT COMPATIBLE) ---
            
            # Brain Factory
            self.lib.sovereign_init_master.argtypes = []
            self.lib.sovereign_init_master.restype = ctypes.c_void_p
            
            # Agent Factory
            self.lib.sovereign_init_agent.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int]
            self.lib.sovereign_init_agent.restype = ctypes.c_void_p
            
            # Observation
            self.lib.sovereign_agent_observe.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            self.lib.sovereign_agent_observe.restype = None
            
            # Action/Inference
            self.lib.sovereign_agent_act.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]
            self.lib.sovereign_agent_act.restype = ctypes.c_char_p
            
            # Initialize Global Brain
            self.master_brain = self.lib.sovereign_init_master()
            
            if not self.master_brain:
                print("[ERROR] Master Brain allocation failed (Memory?).")
                return

            # Initialize Agents
            agent_names = ["Alpha", "Beta", "Delta", "Gamma"]
            for i, name in enumerate(agent_names):
                ptr = self.lib.sovereign_init_agent(name.encode('utf-8'), self.master_brain, 100 * (i+1))
                if ptr:
                    self.agents[name] = ptr
            
            print(f"[SUCCESS] Sovereign Swarm Engine Loaded: {len(self.agents)} agents active.")
        except Exception as e:
            print(f"[ERROR] Critical Bridge Failure: {e}")
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
        "engine": "v1.51 Stabilized",
        "ready_agents": list(engine.agents.keys())
    }

@app.get("/status")
async def get_status():
    return {
        "engine_loaded": engine.lib is not None and engine.master_brain is not None,
        "agents_ready": list(engine.agents.keys())
    }

@app.post("/observe")
async def observe(req: ObserveRequest):
    if not engine.lib or req.agent_id not in engine.agents:
        return {"error": "Engine offline"}
    
    try:
        agent_ptr = engine.agents[req.agent_id]
        engine.lib.sovereign_agent_observe(agent_ptr, req.text.encode('utf-8'))
        return {"status": "ok"}
    except:
        return {"error": "Observation crash"}

@app.post("/act")
async def act(req: ActRequest):
    if not engine.lib or req.agent_id not in engine.agents:
        return {"error": "Engine offline"}
    
    try:
        agent_ptr = engine.agents[req.agent_id]
        # Call into C++
        raw_res = engine.lib.sovereign_agent_act(agent_ptr, req.max_chars, req.temp)
        
        # Decode with safety
        if raw_res:
            content = raw_res.decode('utf-8', errors='ignore')
        else:
            content = "... [Neural Silence] ..."
            
        return {
            "agent": req.agent_id,
            "content": content
        }
    except Exception as e:
        print(f"[CRASH] /act endpoint: {e}")
        return {"error": "Neural Inference Crash"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
