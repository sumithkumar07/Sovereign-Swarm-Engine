# 🎬 2-Minute Demo Walkthrough

Follow these steps to see the **Sovereign Titan Swarm** running on your local machine in under 2 minutes.

## Prerequisites
- **OS**: Windows, Linux, or macOS.
- **Python 3.10+** (For the bridge).
- **Node.js 18+** (For the workbench UI).
- (Optional) **CUDA 12.0+** for maximum performance.

---

## Step 1: Ignite the Neural Engine (45 Seconds)
First, we'll start the local FastAPI bridge which manages the agents.

```bash
cd engine
pip install -r requirements.txt
python main.py
```
*You should see: `[SUCCESS] Sovereign Swarm Engine Loaded: 20 agents active.`*

## Step 2: Launch the Workbench UI (45 Seconds)
In a new terminal window, start the Next.js workbench.

```bash
cd client
npm install
npm run dev
```
*Visit `http://localhost:3000` in your browser.*

## Step 3: Start the Swarm (30 Seconds)
1. On the **Workbench** dashboard, type a "Seed Reality" (e.g., *"What is the impact of decentralized intelligence on local silicon?"*).
2. Click **Start Swarm Pulse**.
3. Watch as the 4 Titan agents (Alpha, Beta, Delta, Gamma) begin an autonomous dialogue in real-time.
4. Export the **Analytical Report** to see how the engine resolved the query.

---

## 📽️ What to Look For
- **Low Latency**: Notice how quickly the text streams (10,000+ TPS potential).
- **Agent Interruption**: Agents have a 20% chance to interrupt each other with lateral ideas.
- **VRAM Usage**: Check your task manager; the 1.5M model uses less than 15MB of VRAM.

---

> *Can't run it locally right now? Check out the [Benchmarks & Results](results/README.md) to see real output fragments and performance metrics.*
