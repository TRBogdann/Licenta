import tkinter as tk
from tkinter import ttk

class Logger(tk.Frame):
    def __init__(self, parent, messages):
        super().__init__(parent, bg="#2e2e2e", padx=10, pady=10)

        self.messages = messages

        self.canvas = tk.Canvas(self, bg="#2e2e2e", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2e2e2e")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.render_messages()

    def render_messages(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for msg in self.messages:
            lbl = tk.Label(
                self.scrollable_frame,
                text=msg,
                wraplength=300,
                justify="left",
                anchor="w",
                bg="#3a3a3a",
                fg="white",
                font=("Segoe UI", 10),
                padx=8, pady=4
            )
            lbl.pack(fill="x", pady=2, anchor="w")

    def add_message(self, msg):
        self.messages.append(msg)
        self.render_messages()
        self.canvas.yview_moveto(1.0)

