import tkinter as tk
from tkinter import ttk, filedialog
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict, Counter
from pathlib import Path
import math
from matplotlib.backends.backend_pdf import PdfPages  # Import for PDF export

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

        # Add Export to PDF button
        self.export_button = ttk.Button(root, text="Export to PDF", command=self.export_to_pdf, state="disabled")
        self.export_button.pack(pady=5)

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
            self.export_button.config(state="normal")  # Enable export button after loading a file
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
        # Create a figure with three subplots: 3D heatmap, 2D visualization, and pie chart
        fig = plt.figure(figsize=(16, 12))

        # 3D Heatmap
        ax1 = fig.add_subplot(221, projection='3d')
        for name, data in self.player_data.items():
            xs, ys, zs = zip(*data["positions"])
            ax1.scatter(xs, ys, zs, label=name, s=10)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax1.set_title('3D Movement Heatmap')

        # 2D Visualization
        ax2 = fig.add_subplot(222)
        for name, data in self.player_data.items():
            # Extract movement positions for the player
            movement_positions = data["positions"]
            if movement_positions:
                x_move, z_move = zip(*[(pos[0], pos[2]) for pos in movement_positions])
                ax2.plot(x_move, z_move, linestyle='dotted', label=f"{name} Movement Path")

        # Extract block placement positions for each player
        block_positions_by_player = defaultdict(list)
        for event in self.events:
            if event["event"] == "BlockPlaced":
                player_name = event["body"]["player"]["name"]
                pos = event["body"]["player"]["position"]
                block_positions_by_player[player_name].append((pos["x"], pos["z"]))

        for name, block_positions in block_positions_by_player.items():
            if block_positions:
                x_blocks, z_blocks = zip(*block_positions)
                ax2.scatter(x_blocks, z_blocks, label=f"{name} Blocks Placed", s=50)

        ax2.set_title("2D Movement and Block Placement")
        ax2.set_xlabel("X Coordinate")
        ax2.set_ylabel("Z Coordinate")
        ax2.legend()
        ax2.grid(True)
        ax2.axis("equal")  # Keep the X and Z scales proportional

        # Pie Chart for Block Types
        ax3 = fig.add_subplot(212)
        block_counts = Counter(
            event["body"]["block"]["id"]
            for event in self.events
            if event["event"] == "BlockPlaced"
        )
        labels = block_counts.keys()
        sizes = block_counts.values()

        ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax3.set_title("Distribution of Block Types Placed")
        ax3.axis('equal')  # Ensures the pie chart is circular

        # Add the combined figure to Tkinter canvas
        heat_canvas = FigureCanvasTkAgg(fig, master=self.output_frame)
        heat_canvas.draw()
        heat_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def export_to_pdf(self):
        """Export the visuals and summary data to a PDF."""
        if not self.events:
            self.file_label.config(text="No data to export.")
            return

        # Ask the user for a file name and location
        file_path = filedialog.asksaveasfilename(
            title="Save PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return  # User canceled the save dialog

        try:
            with PdfPages(file_path) as pdf:
                # Export the summary data
                fig, ax = plt.subplots(figsize=(8.5, 11))  # Standard letter size
                ax.axis("off")  # Turn off the axis
                summary_text = "\n".join([f"{name}: Time = {data['total_time']}s, Blocks = {data['blocks_broken_or_placed']}, Distance = {data['total_distance']} blocks"
                                          for name, data in self.player_data.items()])
                ax.text(0.5, 0.5, summary_text, fontsize=12, ha="center", va="center", wrap=True)
                ax.set_title("Player Activity Summary", fontsize=16)
                pdf.savefig(fig)  # Save the summary page
                plt.close(fig)

                # Export the visuals (heatmap, 2D visualization, and pie chart)
                fig = plt.figure(figsize=(16, 12))
                # Recreate the visuals
                ax1 = fig.add_subplot(221, projection='3d')
                for name, data in self.player_data.items():
                    xs, ys, zs = zip(*data["positions"])
                    ax1.scatter(xs, ys, zs, label=name, s=10)
                ax1.set_xlabel('X')
                ax1.set_ylabel('Y')
                ax1.set_zlabel('Z')
                ax1.set_title('3D Movement Heatmap')

                ax2 = fig.add_subplot(222)
                for name, data in self.player_data.items():
                    movement_positions = data["positions"]
                    if movement_positions:
                        x_move, z_move = zip(*[(pos[0], pos[2]) for pos in movement_positions])
                        ax2.plot(x_move, z_move, linestyle='dotted', label=f"{name} Movement Path")

                block_positions_by_player = defaultdict(list)
                for event in self.events:
                    if event["event"] == "BlockPlaced":
                        player_name = event["body"]["player"]["name"]
                        pos = event["body"]["player"]["position"]
                        block_positions_by_player[player_name].append((pos["x"], pos["z"]))

                for name, block_positions in block_positions_by_player.items():
                    if block_positions:
                        x_blocks, z_blocks = zip(*block_positions)
                        ax2.scatter(x_blocks, z_blocks, label=f"{name} Blocks Placed", s=50)

                ax2.set_title("2D Movement and Block Placement")
                ax2.set_xlabel("X Coordinate")
                ax2.set_ylabel("Z Coordinate")
                ax2.legend()
                ax2.grid(True)
                ax2.axis("equal")

                ax3 = fig.add_subplot(212)
                block_counts = Counter(
                    event["body"]["block"]["id"]
                    for event in self.events
                    if event["event"] == "BlockPlaced"
                )
                labels = block_counts.keys()
                sizes = block_counts.values()

                ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax3.set_title("Distribution of Block Types Placed")
                ax3.axis('equal')

                pdf.savefig(fig)  # Save the visuals page
                plt.close(fig)

            self.file_label.config(text=f"Exported to {file_path}")
        except Exception as e:
            self.file_label.config(text=f"Error exporting to PDF: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftDataLab(root)
    root.mainloop()
