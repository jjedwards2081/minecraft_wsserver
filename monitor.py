import tkinter as tk
from tkinter import filedialog, ttk
import json
from pathlib import Path

class MinecraftMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Live Player Monitor")
        self.root.geometry("500x400")

        self.selected_file = None
        self.player_positions = {}
        self.joined_players = set()
        self.last_data = []

        # UI Layout
        self.label = ttk.Label(root, text="Select event JSON file to monitor:")
        self.label.pack(pady=10)

        self.select_button = ttk.Button(root, text="Browse JSON File", command=self.select_file)
        self.select_button.pack()

        self.status = ttk.Label(root, text="", foreground="blue")
        self.status.pack(pady=5)

        self.output_frame = ttk.Frame(root)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.player_list = tk.Text(self.output_frame, state="disabled", height=20)
        self.player_list.pack(fill=tk.BOTH, expand=True)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select JSON Event File",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.selected_file = Path(file_path)
            self.status.config(text=f"Monitoring: {self.selected_file.name}")
            self.joined_players.clear()
            self.player_positions.clear()
            self.last_data = []
            self.update_loop()

    def update_loop(self):
        if self.selected_file and self.selected_file.exists():
            try:
                with open(self.selected_file, "r") as f:
                    data = json.load(f)
                    if data != self.last_data:
                        self.last_data = data
                        self.process_events(data)
            except Exception as e:
                self.status.config(text=f"Error: {e}", foreground="red")

        self.root.after(2000, self.update_loop)  # Check every 2 seconds

    def process_events(self, events):
        for event in events:
            event_type = event.get("event")
            body = event.get("body", {})

            if event_type == "PlayerJoin":
                player_name = body.get("playerName", "Unknown")
                self.joined_players.add(player_name)

            elif event_type == "PlayerTransform":
                player = body.get("player", {})
                name = player.get("name", "Unknown")
                pos = player.get("position", {})
                if name:
                    self.player_positions[name] = {
                        "x": round(pos.get("x", 0), 1),
                        "y": round(pos.get("y", 0), 1),
                        "z": round(pos.get("z", 0), 1)
                    }
                    self.joined_players.add(name)

            elif event_type == "PlayerMessage":
                name = body.get("sender", "Unknown")
                self.joined_players.add(name)

        self.refresh_display()

    def refresh_display(self):
        self.player_list.config(state="normal")
        self.player_list.delete(1.0, tk.END)

        self.player_list.insert(tk.END, "🧍 Joined Players:\n")
        for name in sorted(self.joined_players):
            self.player_list.insert(tk.END, f"  • {name}\n")

        self.player_list.insert(tk.END, "\n📍 Player Positions:\n")
        for name, pos in self.player_positions.items():
            self.player_list.insert(
                tk.END,
                f"  • {name}: ({pos['x']}, {pos['y']}, {pos['z']})\n"
            )

        self.player_list.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftMonitorApp(root)
    root.mainloop()
