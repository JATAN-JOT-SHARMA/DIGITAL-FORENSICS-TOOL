import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import datetime

from forensic_engine import ForensicEngine
from reports import ReportGenerator


class ForenXUI:

    def __init__(self, root):
        self.root = root
        self.root.title("ForenX AI - Digital Forensics Tool")
        self.root.geometry("1400x800")
        self.root.configure(bg="#111111")

        self.running = False
        self.data = {}

        self.setup_style()
        self.setup_ui()

    def setup_style(self):
        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "TNotebook",
            background="#111111",
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background="#222222",
            foreground="#00ff00",
            padding=[10, 5]
        )

    def setup_ui(self):

        main_frame = tk.Frame(
            self.root,
            bg="#111111"
        )
        main_frame.pack(fill="both", expand=True)

        # =====================
        # LEFT PANEL
        # =====================
        left_panel = tk.Frame(
            main_frame,
            bg="#1a1a1a",
            width=320
        )
        left_panel.pack(
            side="left",
            fill="y"
        )
        left_panel.pack_propagate(False)

        title = tk.Label(
            left_panel,
            text="FORENX AI",
            font=("Consolas", 24, "bold"),
            fg="#00ff00",
            bg="#1a1a1a"
        )
        title.pack(pady=20)

        subtitle = tk.Label(
            left_panel,
            text="Digital Forensics Suite",
            font=("Arial", 10),
            fg="#aaaaaa",
            bg="#1a1a1a"
        )
        subtitle.pack()

        tk.Frame(
            left_panel,
            bg="#00ff00",
            height=2
        ).pack(fill="x", padx=15, pady=20)

        # buttons
        self.create_buttons(left_panel)

        # status
        self.status_label = tk.Label(
            left_panel,
            text="● READY",
            fg="#00ff00",
            bg="#1a1a1a",
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(
            side="bottom",
            pady=20
        )

        # =====================
        # RIGHT PANEL
        # =====================
        right_panel = tk.Frame(
            main_frame,
            bg="#111111"
        )
        right_panel.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.notebook = ttk.Notebook(
            right_panel
        )
        self.notebook.pack(
            fill="both",
            expand=True
        )

        # console tab
        console_tab = tk.Frame(
            self.notebook,
            bg="#111111"
        )

        self.notebook.add(
            console_tab,
            text="Console"
        )

        self.console = scrolledtext.ScrolledText(
            console_tab,
            bg="black",
            fg="#00ff00",
            font=("Consolas", 10),
            insertbackground="#00ff00"
        )
        self.console.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        # results tab
        results_tab = tk.Frame(
            self.notebook,
            bg="#111111"
        )

        self.notebook.add(
            results_tab,
            text="Results"
        )

        self.results_box = scrolledtext.ScrolledText(
            results_tab,
            bg="#0d0d0d",
            fg="#00ff00",
            font=("Consolas", 10)
        )
        self.results_box.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.log("FORENX AI INITIALIZED")
        self.log("Ready for forensic analysis")

    def create_buttons(self, parent):

        btn_style = {
            "font": ("Arial", 12),
            "bg": "#222222",
            "fg": "#00ff00",
            "activebackground": "#333333",
            "activeforeground": "#00ff00",
            "relief": "flat",
            "cursor": "hand2"
        }

        buttons = [
            ("RUN FULL ANALYSIS", self.run_full),
            ("BROWSER HISTORY", self.browser_scan),
            ("USB ANALYSIS", self.usb_scan),
            ("DISK ANALYSIS", self.disk_scan),
            ("EVIDENCE COLLECTOR", self.file_scan),
            ("GENERATE REPORT", self.generate_report),
            ("CLEAR DATA", self.clear_data)
        ]

        for text, command in buttons:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                height=2,
                **btn_style
            )
            btn.pack(
                fill="x",
                padx=20,
                pady=5
            )

    def log(self, message):

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        def update_ui():
            self.console.insert(
                tk.END,
                f"[{timestamp}] {message}\n"
            )
            self.console.see(tk.END)

        self.root.after(0, update_ui)

    def set_status(self, text):
        self.root.after(
            0,
            lambda: self.status_label.config(
                text=text
            )
        )

    def run_thread(self, target):
        if self.running:
            return

        self.running = True
        threading.Thread(
            target=target,
            daemon=True
        ).start()

    def run_full(self):
        self.run_thread(self._run_full)

    def _run_full(self):

        self.set_status("◉ ANALYZING...")

        try:
            engine = ForensicEngine(
                self.log
            )

            self.data = engine.run_full()

            self.show_results()

            self.log(
                "Full analysis completed"
            )

        except Exception as e:
            self.log(f"ERROR: {e}")

        self.running = False
        self.set_status("● READY")

    def browser_scan(self):
        self.log("Browser scan starting...")

    def usb_scan(self):
        self.log("USB scan starting...")

    def disk_scan(self):
        self.log("Disk scan starting...")

    def file_scan(self):
        self.log("Evidence collection started...")

    def generate_report(self):
        if not self.data:
            messagebox.showwarning(
                "No Data",
                "Run analysis first."
            )
            return

        ReportGenerator(
            self.data,
            self.log
        ).generate()

    def clear_data(self):
        self.data = {}
        self.results_box.delete(
            "1.0",
            tk.END
        )
        self.log("Data cleared")

    def show_results(self):

        self.results_box.delete(
            "1.0",
            tk.END
        )

        self.results_box.insert(
            tk.END,
            str(self.data)
        )