import tkinter as tk
from tkinter import ttk, filedialog
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict, Counter
from pathlib import Path
import math
from openai import AzureOpenAI
import os
from matplotlib.backends.backend_pdf import PdfPages  # Import for PDF export

class PlayerAssessmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Player Assessment")
        self.root.geometry("1200x800")  # Increased width to accommodate text boxes

        # Azure OpenAI Configuration
        self.azure_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  # Set your API key in environment variables
            api_version="2024-10-21",  # Use the correct API version
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")  # Set your endpoint in environment variables
        )

        self.events = []
        self.player_data = defaultdict(lambda: {
            "total_time": 0,  # time spent
            "blocks_broken_or_placed": 0,  # blocks placed or broken
            "total_distance": 0,  # distance traveled
            "positions": []  # list of positions
        })
        self.selected_file = None
        self.selected_player = tk.StringVar()

        # UI setup
        self.file_label = ttk.Label(root, text="No file selected")
        self.file_label.pack(pady=5)

        self.select_button = ttk.Button(root, text="Load Log File", command=self.load_file)
        self.select_button.pack(pady=5)

        self.player_dropdown = ttk.Combobox(root, textvariable=self.selected_player, state="readonly")
        self.player_dropdown.pack(pady=5)
        self.player_dropdown.bind("<<ComboboxSelected>>", self.run_analysis)

        # Button frame for horizontal alignment
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        self.analyze_button = ttk.Button(button_frame, text="Run Analysis", command=self.run_analysis, state="disabled")
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        self.quit_button = ttk.Button(button_frame, text="Quit", command=root.quit)
        self.quit_button.pack(side=tk.LEFT, padx=5)

        # Main frame for graphs and text boxes
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame for graphs
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.output_frame = ttk.Frame(graph_frame)
        self.output_frame.pack(fill=tk.BOTH, expand=True)

        # Frame for text boxes
        text_box_frame = ttk.Frame(main_frame)
        text_box_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        # Text box 1: Assessment Requirements
        self.assessment_label = ttk.Label(text_box_frame, text="Assessment Requirements")
        self.assessment_label.pack(pady=5)
        self.assessment_text = tk.Text(text_box_frame, height=10, width=40)
        self.assessment_text.pack(pady=5)
        self.run_button = ttk.Button(text_box_frame, text="Run", command=self.run_assessment)
        self.run_button.pack(pady=5)

        # Text box 2: Criteria / Rubric
        self.criteria_label = ttk.Label(text_box_frame, text="Criteria / Rubric")
        self.criteria_label.pack(pady=5)
        self.criteria_text = tk.Text(text_box_frame, height=10, width=40)
        self.criteria_text.pack(pady=5)
        self.accept_button = ttk.Button(text_box_frame, text="Accept", command=self.accept_criteria, state="disabled")
        self.accept_button.pack(pady=5)

        # Text box 3: Result
        self.result_label = ttk.Label(text_box_frame, text="Result")
        self.result_label.pack(pady=5)
        self.result_text = tk.Text(text_box_frame, height=10, width=40, state="disabled")
        self.result_text.pack(pady=5)
        self.pdf_button = ttk.Button(text_box_frame, text="Export to PDF", command=self.export_to_pdf)
        self.pdf_button.pack(pady=5)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Minecraft Log File",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.selected_file = Path(file_path)
            self.file_label.config(text=f"Loaded: {self.selected_file.name}")
            self.analyze_button.config(state="normal")
            self.load_events()

    def load_events(self):
        try:
            with open(self.selected_file, "r") as f:
                self.events = json.load(f)
        except Exception as e:
            self.file_label.config(text=f"Error reading file: {e}")
            return

        # Populate the dropdown with player names
        player_names = set(
            event["body"]["player"]["name"]
            for event in self.events
            if "player" in event.get("body", {})
        )
        self.player_dropdown["values"] = list(player_names)
        if player_names:
            self.player_dropdown.current(0)  # Select the first player by default

    def run_analysis(self, event=None):
        selected_player = self.selected_player.get()
        if not selected_player:
            self.file_label.config(text="No player selected.")
            return

        # Reset player data for the selected player
        self.player_data.clear()

        # Process events for the selected player
        for event in self.events:
            etype = event.get("event")
            body = event.get("body", {})
            player = body.get("player", {})
            name = player.get("name", "Unknown")

            if name != selected_player:
                continue

            if etype == "PlayerTransform":
                pos = player.get("position", {})
                x, y, z = pos.get("x"), pos.get("y"), pos.get("z")
                if None not in (x, y, z):
                    self.player_data[name]["positions"].append((x, y, z))
                    self.player_data[name]["total_time"] += 1  # increment time spent
                    if len(self.player_data[name]["positions"]) > 1:
                        self.player_data[name]["total_distance"] += self.calculate_distance(self.player_data[name]["positions"][-2:])
            
            elif etype == "BlockPlaced" or etype == "BlockBroken":
                self.player_data[name]["blocks_broken_or_placed"] += 1

        # Clear previous output
        for widget in self.output_frame.winfo_children():
            widget.destroy()

        # Display summary of player activities
        summary_text = "\n".join([f"{name}: Time = {data['total_time']}s, Blocks = {data['blocks_broken_or_placed']}, Distance = {data['total_distance']} blocks" 
                                  for name, data in self.player_data.items()])
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, summary_text)
        self.result_text.config(state="disabled")

        # Heatmap visualization
        self.display_heatmap(selected_player)

    def calculate_distance(self, positions):
        dist = 0
        x1, y1, z1 = positions[0]
        x2, y2, z2 = positions[1]
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        return dist

    def display_heatmap(self, player_name):
        # Create a figure with two subplots: 2D visualization and pie chart
        fig = plt.figure(figsize=(6, 3))  # Reduced size by 50%

        # 2D Visualization
        ax1 = fig.add_subplot(121)
        data = self.player_data[player_name]
        movement_positions = data["positions"]
        if movement_positions:
            x_move, z_move = zip(*[(pos[0], pos[2]) for pos in movement_positions])
            ax1.plot(x_move, z_move, linestyle='dotted', label="Movement Path")

        # Add block placements as circles
        block_positions = [
            (event["body"]["player"]["position"]["x"], event["body"]["player"]["position"]["z"])
            for event in self.events
            if event["event"] == "BlockPlaced" and event["body"]["player"]["name"] == player_name
        ]
        if block_positions:
            x_blocks, z_blocks = zip(*block_positions)
            ax1.scatter(x_blocks, z_blocks, color='blue', label="Block Placements", s=50, alpha=0.7)

        ax1.set_title(f"2D Movement for {player_name}")
        ax1.set_xlabel("X Coordinate")
        ax1.set_ylabel("Z Coordinate")
        ax1.legend()
        ax1.grid(True)
        ax1.axis("equal")

        # Pie Chart for Block Types
        ax2 = fig.add_subplot(122)
        block_counts = Counter(
            event["body"]["block"]["id"]
            for event in self.events
            if event["event"] == "BlockPlaced" and event["body"]["player"]["name"] == player_name
        )
        labels = block_counts.keys()
        sizes = block_counts.values()

        ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax2.set_title(f"Block Types Placed by {player_name}")
        ax2.axis('equal')

        # Add the figure to Tkinter canvas
        heat_canvas = FigureCanvasTkAgg(fig, master=self.output_frame)
        heat_canvas.draw()
        heat_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_assessment(self):
        """Process the 'Assessment Requirements' text using Azure AI."""
        assessment_text = self.assessment_text.get("1.0", tk.END).strip()
        if not assessment_text:
            self.criteria_text.config(state="normal")
            self.criteria_text.delete("1.0", tk.END)
            self.criteria_text.insert(tk.END, "Please enter assessment requirements.")
            self.criteria_text.config(state="disabled")
            return

        try:
            # Send the assessment text to Azure OpenAI
            response = self.azure_client.chat.completions.create(
                model="gpt-4o",  # Replace with your deployment name
                messages=[
                    {"role": "system", "content": "You are an AI assistant that generates criteria or rubrics based on assessment requirements."},
                    {"role": "user", "content": assessment_text}
                ]
            )

            # Extract the AI's response
            ai_response = response.choices[0].message.content

            # Display the response in the "Criteria / Rubric" text box
            self.criteria_text.config(state="normal")
            self.criteria_text.delete("1.0", tk.END)
            self.criteria_text.insert(tk.END, ai_response)
            self.criteria_text.config(state="disabled")

            # Enable the "Accept" button
            self.accept_button.config(state="normal")

        except Exception as e:
            self.criteria_text.config(state="normal")
            self.criteria_text.delete("1.0", tk.END)
            self.criteria_text.insert(tk.END, f"Error: {e}")
            self.criteria_text.config(state="disabled")

    def accept_criteria(self):
        """Send the selected player's data and criteria to Azure AI for assessment."""
        selected_player = self.selected_player.get()
        if not selected_player:
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "No player selected.")
            self.result_text.config(state="disabled")
            return

        criteria_text = self.criteria_text.get("1.0", tk.END).strip()
        if not criteria_text:
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "No criteria available.")
            self.result_text.config(state="disabled")
            return

        # Get the JSON data for the selected player
        player_data = self.player_data[selected_player]

        try:
            # Send the player data and criteria to Azure OpenAI
            response = self.azure_client.chat.completions.create(
                model="gpt-4o",  # Replace with your deployment name
                messages=[
                    {"role": "system", "content": "You are an AI assistant that assesses Minecraft player data against a given criteria or rubric."},
                    {"role": "user", "content": f"Criteria: {criteria_text}\n\nPlayer Data: {json.dumps(player_data)}"}
                ]
            )

            # Extract the AI's response
            ai_response = response.choices[0].message.content

            # Display the response in the "Result" text box
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, ai_response)
            self.result_text.config(state="disabled")

        except Exception as e:
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Error: {e}")
            self.result_text.config(state="disabled")

    def export_to_pdf(self):
        """Export the graphs, criteria, and result to a PDF."""
        selected_player = self.selected_player.get()
        if not selected_player:
            self.file_label.config(text="No player selected for PDF export.")
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
                # Add a header page
                fig, ax = plt.subplots(figsize=(8.5, 11))  # Standard letter size
                ax.axis("off")  # Turn off the axis
                ax.text(0.5, 0.9, f"Assessment of Player: {selected_player}", fontsize=16, ha="center", va="center")
                pdf.savefig(fig)
                plt.close(fig)

                # Add the graphs
                fig = plt.figure(figsize=(6, 3))  # Reduced size by 50%
                ax1 = fig.add_subplot(121)
                data = self.player_data[selected_player]
                movement_positions = data["positions"]
                if movement_positions:
                    x_move, z_move = zip(*[(pos[0], pos[2]) for pos in movement_positions])
                    ax1.plot(x_move, z_move, linestyle='dotted', label="Movement Path")
                block_positions = [
                    (event["body"]["player"]["position"]["x"], event["body"]["player"]["position"]["z"])
                    for event in self.events
                    if event["event"] == "BlockPlaced" and event["body"]["player"]["name"] == selected_player
                ]
                if block_positions:
                    x_blocks, z_blocks = zip(*block_positions)
                    ax1.scatter(x_blocks, z_blocks, color='blue', label="Block Placements", s=50, alpha=0.7)
                ax1.set_title(f"2D Movement for {selected_player}")
                ax1.set_xlabel("X Coordinate")
                ax1.set_ylabel("Z Coordinate")
                ax1.legend()
                ax1.grid(True)
                ax1.axis("equal")

                ax2 = fig.add_subplot(122)
                block_counts = Counter(
                    event["body"]["block"]["id"]
                    for event in self.events
                    if event["event"] == "BlockPlaced" and event["body"]["player"]["name"] == selected_player
                )
                labels = block_counts.keys()
                sizes = block_counts.values()
                ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax2.set_title(f"Block Types Placed by {selected_player}")
                ax2.axis('equal')
                pdf.savefig(fig)
                plt.close(fig)

                # Add the criteria and result
                fig, ax = plt.subplots(figsize=(8.5, 11))
                ax.axis("off")
                criteria_text = self.criteria_text.get("1.0", tk.END).strip()
                result_text = self.result_text.get("1.0", tk.END).strip()
                content = f"Criteria / Rubric:\n\n{criteria_text}\n\nResult:\n\n{result_text}"
                ax.text(0.5, 0.5, content, fontsize=12, ha="center", va="center", wrap=True)
                pdf.savefig(fig)
                plt.close(fig)

            self.file_label.config(text=f"Exported to {file_path}")
        except Exception as e:
            self.file_label.config(text=f"Error exporting to PDF: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerAssessmentApp(root)
    root.mainloop()