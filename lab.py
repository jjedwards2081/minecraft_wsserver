import tkinter as tk
from tkinter import ttk, filedialog
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict, Counter
from pathlib import Path
import math

class MinecraftDataLab:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Data Science Lab")
        self.root.geometry("900x800")

        self.events = []
        self.player_data = defaultdict(lambda: {
            "total_time": 0,  # time spent
            "blocks_broken_or_placed": 0,  # blocks placed or broken
            "total_distance": 0,  # distance traveled
            "positions": []  # list of positions
        })
        self.selected_file = None

        # UI setup
        self.file_label = ttk.Label(root, text="No file selected")
        self.file_label.pack(pady=5)

        self.select_button = ttk.Button(root, text="Load Log File", command=self.load_file)
        self.select_button.pack(pady=5)

        self.analyze_button = ttk.Button(root, text="Run Analysis", command=self.run_analysis, state="disabled")
        self.analyze_button.pack(pady=10)

        self.quit_button = ttk.Button(root, text="Quit", command=root.quit)
        self.quit_button.pack(pady=5)

        self.output_frame = ttk.Frame(root)
        self.output_frame.pack(fill=tk.BOTH, expand=True)

        self.summary_label = ttk.Label(root, text="Player Activity Summary")
        self.summary_label.pack(pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Minecraft Log File",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.selected_file = Path(file_path)
            self.file_label.config(text=f"Loaded: {self.selected_file.name}")
            self.analyze_button.config(state="normal")
            self.run_analysis()

    def run_analysis(self):
        try:
            with open(self.selected_file, "r") as f:
                self.events = json.load(f)
        except Exception as e:
            self.file_label.config(text=f"Error reading file: {e}")
            return

        # Reset player data for each analysis
        self.player_data.clear()

        # Process events
        for event in self.events:
            etype = event.get("event")
            body = event.get("body", {})

            if etype == "PlayerMessage":
                # Handle player messages if needed (not required in this case)
                pass

            elif etype == "PlayerTransform":
                player = body.get("player", {})
                name = player.get("name", "Unknown")
                pos = player.get("position", {})
                x, y, z = pos.get("x"), pos.get("y"), pos.get("z")
                if None not in (x, y, z):
                    self.player_data[name]["positions"].append((x, y, z))
                    self.player_data[name]["total_time"] += 1  # increment time spent
                    if len(self.player_data[name]["positions"]) > 1:
                        self.player_data[name]["total_distance"] += self.calculate_distance(self.player_data[name]["positions"][-2:])
            
            elif etype == "BlockPlaced" or etype == "BlockBroken":
                # Assuming a block placed/broken event
                player = body.get("player", {})
                name = player.get("name", "Unknown")
                if name in self.player_data:
                    self.player_data[name]["blocks_broken_or_placed"] += 1

        # Clear previous output
        for widget in self.output_frame.winfo_children():
            widget.destroy()

        # Display summary of player activities
        summary_text = "\n".join([f"{name}: Time = {data['total_time']}s, Blocks = {data['blocks_broken_or_placed']}, Distance = {data['total_distance']} blocks" 
                                  for name, data in self.player_data.items()])
        self.summary_label.config(text=summary_text)

        # Heatmap visualization
        self.display_heatmap()

    def calculate_distance(self, positions):
        dist = 0
        x1, y1, z1 = positions[0]
        x2, y2, z2 = positions[1]
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        return dist

    def display_heatmap(self):
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')

        # Plot each player's positions in 3D space
        for name, data in self.player_data.items():
            xs, ys, zs = zip(*data["positions"])
            ax.scatter(xs, ys, zs, label=name, s=10)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('3D Player Movement Heatmap')

        # Add the heatmap to Tkinter canvas
        heat_canvas = FigureCanvasTkAgg(fig, master=self.output_frame)
        heat_canvas.draw()
        heat_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftDataLab(root)
    root.mainloop()
