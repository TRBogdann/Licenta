import os
import threading
import time
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk

from logger import Logger
from mri_analyzer import createMask
from reader import create3DModel, save_rmn_slices_as_png


class App:
    def __init__(self) -> None:
        self.paths = [None for _ in range(5)]

        self.root = tk.Tk()
        self.root.title("MRI-Analyzer")
        self.root.geometry("1000x800")
        icon_image = tk.PhotoImage(file="../logo.png")
        self.root.iconphoto(False, icon_image)
        self.root.resizable(True, True)
        self.root.configure(bg="#e9ecef")

        self.state = "none"

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 11), padding=8)
        self.style.configure(
            "Primary.TButton", background="#0078D7", foreground="white"
        )
        self.style.map("Primary.TButton", background=[("active", "#005a9e")])

        self.style.configure(
            "Danger.TButton", background="#d9534f", foreground="white"
        )
        self.style.map("Danger.TButton", background=[("active", "#b52b27")])

        self.style.configure(
            "Card.TFrame", background="white", relief="solid", borderwidth=1
        )

        self.load()

    def load(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        top_frame = ttk.Frame(self.root, style="Card.TFrame", padding=15)
        top_frame.pack(side="top", fill="x", pady=20, padx=20)

        ttk.Button(
            top_frame,
            text="Generate Masks",
            style="Primary.TButton",
            command=lambda: self.setState("generate"),
        ).pack(side="left", padx=20)

        ttk.Button(
            top_frame,
            text="Load Masks",
            style="Danger.TButton",
            command=lambda: self.setState("load"),
        ).pack(side="left", padx=20)

        content_frame = ttk.Frame(self.root, style="Card.TFrame", padding=25)
        content_frame.pack(expand=True, fill="both", padx=20, pady=10)

        if self.state == "generate":
            self.renderGenerate(content_frame)
        elif self.state == "load":
            self.renderLoad(content_frame)
        else:
            ttk.Label(
                content_frame,
                text="Please select an option above to begin.",
                font=("Segoe UI", 14),
                background="white",
            ).pack(expand=True)

    def dummy(self):
        pass

    def renderLoad(self, parent):
        ttk.Label(
            parent,
            text="Load Existing Masks",
            font=("Segoe UI", 14, "bold"),
            background="white",
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Button(
            parent, text="Load MRI file", command=lambda: self.getFile(0)
        ).grid(row=1, column=0, pady=5, sticky="ew")
        ttk.Label(
            parent,
            text=(
                "No Path"
                if self.paths[0] is None
                else self.trimFilepath(self.paths[0], 30)
            ),
            background="white",
        ).grid(row=1, column=1, padx=10)

        ttk.Button(
            parent, text="Load Masks file", command=lambda: self.getFile(4)
        ).grid(row=2, column=0, pady=5, sticky="ew")
        ttk.Label(
            parent,
            text=(
                "No Path"
                if self.paths[4] is None
                else self.trimFilepath(self.paths[4], 30)
            ),
            background="white",
        ).grid(row=2, column=1, padx=10)

        ttk.Button(
            parent,
            text="Start program",
            style="Primary.TButton",
            command=self.startAnalyzer,
        ).grid(row=5, column=0, columnspan=2, pady=30, ipadx=20)

        for i in range(6):
            parent.grid_rowconfigure(i, weight=0)
        for j in range(2):
            parent.grid_columnconfigure(j, weight=1)

    def renderGenerate(self, parent):
        ttk.Label(
            parent,
            text="Generate Masks - MRI Inputs",
            font=("Segoe UI", 14, "bold"),
            background="white",
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        labels = ["Load T1", "Load T2", "Load T1CE", "Load FLAIIR"]
        for i, lbl in enumerate(labels, start=1):
            index = i - 1
            ttk.Button(
                parent, text=lbl, command=lambda: self.getFile(index)
            ).grid(row=i, column=0, pady=5, sticky="ew")
            ttk.Label(
                parent,
                text=(
                    "No Path"
                    if self.paths[index] is None
                    else self.trimFilepath(self.paths[index], 30)
                ),
                background="white",
            ).grid(row=i, column=1, padx=10)

        ttk.Label(
            parent, text="Choose method for rendering:", background="white"
        ).grid(row=6, column=0, pady=(20, 5), sticky="w")
        self.method_var = tk.StringVar(value="T1")
        method_box = ttk.Combobox(
            parent,
            textvariable=self.method_var,
            values=["T1", "T2", "T1CE", "FLAIIR"],
            state="readonly",
        )
        method_box.grid(row=6, column=1, sticky="ew", pady=(20, 5))

        ttk.Button(
            parent,
            text="Start program",
            style="Primary.TButton",
            command=self.startAnalyzer,
        ).grid(row=7, column=0, columnspan=2, pady=30, ipadx=20)

        for i in range(8):
            parent.grid_rowconfigure(i, weight=0)
        for j in range(2):
            parent.grid_columnconfigure(j, weight=1)

    def start(self):
        self.root.mainloop()

    def trimFilepath(self, filepath, maxChar=15):
        filepath = list(filepath)
        start = len(filepath) - 1 - maxChar
        end = len(filepath)

        if len(filepath) > maxChar:
            filepath[start] = "."
            filepath[start + 1] = "."
            filepath[start + 2] = "."

        return "".join(filepath[start:end])

    def setState(self, newState):
        if self.state != newState:
            self.paths = [None for _ in range(5)]
            self.state = newState
            self.load()

    def getFile(self, index):
        filetypes = (("NII files", "*.nii"), ("All files", "*.*"))

        filename = fd.askopenfilename(
            title="Select NII file",
            initialdir=os.environ["HOME"],
            filetypes=filetypes,
        )

        self.paths[index] = filename
        self.load()

    def __startAsync(self, logger):
        outputModel = os.environ["HOME"] + "/mri-res/brain.obj"
        if self.state == "generate":
            createMask(logger.add_message, self.paths[::-1])
            values = ["T1", "T2", "T1CE", "FLAIIR"]
            method = values.index(self.method_var.get())
            mriPath = self.paths[method]
            maskPath = os.environ["HOME"] + "/mri-res/segmentation.nii"

            create3DModel(logger.add_message, mriPath, outputModel)
            for i in range(3):
                save_rmn_slices_as_png(
                    logger.add_message,
                    mriPath,
                    os.environ["HOME"] + f"/mri-res/slices/axis_{i}",
                    i,
                )
                save_rmn_slices_as_png(
                    logger.add_message,
                    maskPath,
                    os.environ["HOME"] + f"/mri-res/masks/axis_{i}",
                    i,
                    True,
                )

        if self.state == "load":
            create3DModel(logger.add_message, self.paths[0], outputModel)
            for i in range(3):
                save_rmn_slices_as_png(
                    logger.add_message,
                    self.paths[0],
                    os.environ["HOME"] + f"/mri-res/slices/axis_{i}",
                    i,
                )
                save_rmn_slices_as_png(
                    logger.add_message,
                    self.paths[4],
                    os.environ["HOME"] + f"/mri-res/masks/axis_{i}",
                    i,
                    True,
                )

        time.sleep(5)
        os.system("../mri-viewer/build/program")

    def startAnalyzer(self):

        if self.state == "generate":
            for i in range(4):
                if self.paths[i] == None:
                    tk.messagebox.showerror(
                        "Error",
                        "To generate mask you need all 4 methods(T1/T2/T1CE/FLAIIR)",
                    )
                    return

        if self.state == "load":
            if self.paths[0] == None:
                tk.messagebox.showerror("Error", "Missing brain scan")
                return

            if self.paths[4] == None:
                tk.messagebox.showerror("Error", "Missing masks")
                return

        for widget in self.root.winfo_children():
            widget.destroy()
        messages = ["[*] Process started. "]
        logger = Logger(self.root, messages)
        logger.pack(fill="both", expand=True, padx=10, pady=10)

        thread = threading.Thread(target=self.__startAsync, args=(logger,))
        thread.start()
