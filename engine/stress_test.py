import requests
import threading
import time

def call_act(agent_id):
    try:
        r = requests.post("http://localhost:7860/act", json={"agent_id": agent_id, "max_chars": 50, "temp": 0.7})
        if r.status_code == 200:
            print(f"[{agent_id}] Success: {r.json()['content'][:30]}...")
        else:
            print(f"[{agent_id}] Failed: {r.status_code}")
    except Exception as e:
        print(f"[{agent_id}] Error: {e}")

if __name__ == "__main__":
    print("[STRESS TEST] Launching 20 parallel agent interactions...")
    # Hit the first 20 agents (personalities.json usually has 100)
    agent_names = [f"Aura", "Nova", "Cipher", "Vortex", "Flux", "Nexus"] # Just some test names
    
    threads = []
    for name in agent_names:
        t = threading.Thread(target=call_act, args=(name,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print("[STRESS TEST] Completed. Check server logs for any crashes.")
