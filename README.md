## 🧱 Minecraft Education WebSocket Server + Data Science Lab

A Python-powered system that captures player behavior from Minecraft Education Edition and visualizes it in real time using charts, maps, and live tracking interfaces.

### 📜 License

This project is licensed under the MIT License. See the full license text below:

```
MIT License

Copyright (c) 2025 Justin Edwards

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

### ✍️ Author

Created by **Justin Edwards**  
📧 Email: [jnredwards@gmail.com](mailto:jnredwards@gmail.com)

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

4. **AI-Powered Assessment** (`assessment.py`)  
   A script that connects to Azure AI to analyze player behavior and provide insights:
   - Requires an Azure API key and endpoint
   - Generates advanced analytics

---

### 🛠 Setup

#### ✅ Requirements

Install these via pip (preferably in a virtual environment):

```bash
pip install websockets matplotlib azure-ai-textanalytics
```

You also need:

- Python 3.7+
- Minecraft Education Edition (on another device on the same network)
- `allowDebugging=true` in Minecraft settings
- Azure AI API key and endpoint (see below)

#### 🐍 Activate venv (if using one)

```bash
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate     # Windows
```

#### 🔑 Azure AI Setup

To use `assessment.py`, you need an Azure AI API key and endpoint:

1. Go to the [Azure Portal](https://portal.azure.com/).
2. Create a new resource for "Cognitive Services" or "Text Analytics."
3. Copy the **API Key** and **Endpoint** from the resource's "Keys and Endpoint" section.
4. Set these as environment variables in your system:

  ```bash
  export AZURE_API_KEY=your_api_key_here
  export AZURE_ENDPOINT=https://your_endpoint_here
  ```

  On Windows, use:

  ```cmd
  set AZURE_API_KEY=your_api_key_here
  set AZURE_ENDPOINT=https://your_endpoint_here
  ```

---

### 🚀 Running the Server

```bash
python run.py
```

This script will activate the virtual environment (if configured) and start the WebSocket server.

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

### 🤖 Run the AI Assessment

```bash
python assessment.py
```

- Prompts the user to input assessment criteria (e.g., minimum engagement score, sentiment thresholds).
- Requires a `.json` event file from `/data`.
- Compares player data against the provided criteria.
- Outputs results to the console or saves them to a new file in `/data`.

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

AI assessment output example:

```json
{
  "player": "JustinE",
  "sentiment": "positive",
  "engagement_score": 85
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
├── assessment.py         # AI-powered analysis
├── data/                 # JSON logs saved here
└── README.md             # This file
```

---

### 📡 Credits

Built using:
- Python `websockets`
- Tkinter
- Matplotlib
- Azure AI Text Analytics
- Minecraft Education Edition Debug WebSocket API

---