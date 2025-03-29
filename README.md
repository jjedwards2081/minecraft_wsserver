## 🧱 Minecraft Education WebSocket Server + Data Science Lab

A Python-powered system that captures player behavior from Minecraft Education Edition and visualizes it in real time using charts, maps, and live tracking interfaces.

---

### 📦 What's Included

1. **WebSocket Server** (`main.py`)  
   Receives events from Minecraft Education Edition via WebSocket and logs them to a timestamped JSON file in the `/data` folder.

2. **Data Science Lab** (`lab.py`)  
   A Tkinter desktop app that loads and analyzes the captured event data:
   - Total distance walked
   - Average chat message length
   - Word frequency histograms
   - Heatmap of player movement (X/Z grid)
   - Auto-refreshes every 60 seconds after file selection
   - Quit button included

3. **Live Player Monitor** (`monitor.py`)  
   A lightweight Tkinter tool that:
   - Monitors a selected event file
   - Displays who’s joined and their current position
   - Updates every 2 seconds

---

### 🛠 Setup

#### ✅ Requirements

Install these via pip (preferably in a virtual environment):

```bash
pip install websockets matplotlib
```

You also need:

- Python 3.7+
- Minecraft Education Edition (on another device on the same network)
- `allowDebugging=true` in Minecraft settings

#### 🐍 Activate venv (if using one)

```bash
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate     # Windows
```

---

### 🚀 Running the Server

```bash
python main.py
```

- Listens on port `19131`
- Creates a new JSON file like `events_2025-03-28T10-05-22.json` in `/data`
- Logs: PlayerJoin, PlayerLeave, PlayerMessage, PlayerTransform, BlockPlaced

---

### 🧪 Launch the Data Lab

```bash
python lab.py
```

- Click **"Load Log File"** and choose a `.json` event file from `/data`
- Click **"Run Analysis"** or wait for the app to refresh every 60 seconds
- Use **"Quit"** to exit

---

### 👀 Use the Live Player Monitor

```bash
python monitor.py
```

- Select the same JSON file
- See a live display of:
  - Players who joined
  - Their latest known X/Y/Z positions
- Updates every 2 seconds

---

### 🗃 Output Example

Event data looks like:

```json
{
  "event": "PlayerTransform",
  "body": {
    "player": {
      "name": "JustinE",
      "position": { "x": -45.1, "y": 73.6, "z": 66.2 }
    }
  },
  "timestamp": "2025-03-28T10:18:30.340650",
  "client_ip": "192.168.1.10"
}
```

---

### 📁 Folder Structure

```
minecraft_wsserver/
├── server/
│   └── main.py           # WebSocket event logger
├── lab.py                # Data science dashboard
├── monitor.py            # Live player tracker
├── data/                 # JSON logs saved here
└── README.md             # This file
```

---

### 💡 Ideas for Extensions

- Add region-specific analytics (like time spent near 0,0)
- Export reports to PDF/CSV
- Add interactive map using a GUI canvas
- Real-time dashboard with Flask + WebSockets

---

### 📡 Credits

Built using:
- Python `websockets`
- Tkinter
- Matplotlib
- Minecraft Education Edition Debug WebSocket API

---