import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# File to persist data
DATA_FILE = "concepts.json"

# ---------- Core Data Functions ----------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------- App ----------

class ConceptCrafterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ConceptCrafter")
        self.root.geometry("900x600")
        self.data = load_data()

        self.style = ttk.Style()
        self.style.configure("TButton",
            background="#7B241C", foreground="#F7DC6F",
            font=("Segoe UI", 10, "bold"))
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.create_create_tab()
        self.create_manage_tab()
        self.create_test_tab()
        self.create_analysis_tab()

    # ---------- Create Tab ----------
    def create_create_tab(self):
        self.create_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.create_tab, text="Create Concept")

        fields = [
            ("Title", "title"),
            ("Academic Explanation", "academic"),
            ("Your Understanding", "understanding"),
            ("Write a Question for Future Revision", "question"),
            ("Tags (comma separated)", "tags")
        ]

        self.entries = {}
        for label, key in fields:
            ttk.Label(self.create_tab, text=label + ":").pack(anchor="w", padx=10, pady=(10, 0))
            entry = tk.Text(self.create_tab, height=2 if "Explanation" not in label else 4, width=100)
            entry.pack(padx=10, pady=5)
            self.entries[key] = entry

        self.create_button = tk.Button(self.create_tab, text="Save Concept", command=self.save_concept,
                                       bg="#7B241C", fg="#F7DC6F", activebackground="#922B21", font=("Segoe UI", 10, "bold"))
        self.create_button.pack(pady=10)

    def save_concept(self):
        concept = {k: v.get("1.0", "end").strip() for k, v in self.entries.items()}
        concept["timestamp"] = datetime.now().isoformat()
        self.data.append(concept)
        save_data(self.data)
        messagebox.showinfo("Saved", "Concept saved successfully.")
        for entry in self.entries.values():
            entry.delete("1.0", "end")

    # ---------- Manage Tab ----------
    def create_manage_tab(self):
        self.manage_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manage_tab, text="Manage Notes")

        self.search_var = tk.StringVar()
        search_frame = ttk.Frame(self.manage_tab)
        search_frame.pack(pady=10)
        ttk.Label(search_frame, text="Search:").pack(side="left")
        tk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.search_notes,
                  bg="#7B241C", fg="#F7DC6F", activebackground="#922B21", font=("Segoe UI", 10, "bold")).pack(side="left")

        self.results_box = tk.Listbox(self.manage_tab, width=120, height=20)
        self.results_box.pack(pady=10)

        delete_btn = tk.Button(self.manage_tab, text="Delete Selected",
                               command=self.delete_selected,
                               bg="#7B241C", fg="#F7DC6F", activebackground="#922B21", font=("Segoe UI", 10, "bold"))
        delete_btn.pack()

        export_frame = ttk.Frame(self.manage_tab)
        export_frame.pack(pady=10)
        self.export_type = tk.StringVar(value="csv")
        for label in ["CSV", "TXT", "Markdown"]:
            ttk.Radiobutton(export_frame, text=label, variable=self.export_type, value=label.lower()).pack(side="left")
        tk.Button(self.manage_tab, text="Export", command=self.export_results,
                  bg="#7B241C", fg="#F7DC6F", activebackground="#922B21", font=("Segoe UI", 10, "bold")).pack()

        self.search_notes()

    def search_notes(self):
        query = self.search_var.get().lower()
        self.results_box.delete(0, "end")
        self.matched = []
        for concept in self.data:
            if any(query in str(concept[key]).lower() for key in ["title", "academic", "understanding", "tags"]):
                self.results_box.insert("end", f"{concept['title']} | {concept['timestamp']}")
                self.matched.append(concept)
            elif not query:
                self.results_box.insert("end", f"{concept['title']} | {concept['timestamp']}")
                self.matched.append(concept)

    def delete_selected(self):
        selection = self.results_box.curselection()
        if not selection:
            return
        idx = selection[0]
        concept = self.matched[idx]
        self.data.remove(concept)
        save_data(self.data)
        self.search_notes()

    def export_results(self):
        concepts = self.matched
        filetypes = {
            "csv": ("Concepts.csv", self.export_csv),
            "txt": ("Concepts.txt", self.export_txt),
            "markdown": ("Concepts.md", self.export_md)
        }
        filename, method = filetypes[self.export_type.get()]
        method(concepts, filename)
        messagebox.showinfo("Exported", f"Exported to {filename}")

    def export_csv(self, concepts, filename):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Academic", "Understanding", "Question", "Tags", "Timestamp"])
            for c in concepts:
                writer.writerow([c["title"], c["academic"], c["understanding"], c["question"], c["tags"], c["timestamp"]])

    def export_txt(self, concepts, filename):
        with open(filename, "w") as f:
            for c in concepts:
                f.write(f"Title: {c['title']}\nAcademic: {c['academic']}\nUnderstanding: {c['understanding']}\n"
                        f"Question: {c['question']}\nTags: {c['tags']}\nTimestamp: {c['timestamp']}\n\n")

    def export_md(self, concepts, filename):
        with open(filename, "w") as f:
            for c in concepts:
                f.write(f"### {c['title']}\n- **Academic**: {c['academic']}\n- **Understanding**: {c['understanding']}\n"
                        f"- **Question**: {c['question']}\n- **Tags**: {c['tags']}\n- **Timestamp**: {c['timestamp']}\n\n")

    # ---------- Test & Recall Tab ----------
    def create_test_tab(self):
        self.test_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.test_tab, text="Test & Recall")

        ttk.Label(self.test_tab, text="Select Concept Title:").pack(pady=5)
        self.selected_title = tk.StringVar()
        self.title_dropdown = ttk.Combobox(self.test_tab, textvariable=self.selected_title, width=50)
        self.title_dropdown.pack()

        self.refresh_dropdown()

        tk.Button(self.test_tab, text="Start Test", command=self.start_test,
                  bg="#7B241C", fg="#F7DC6F", activebackground="#922B21", font=("Segoe UI", 10, "bold")).pack(pady=10)

        self.q_label = tk.Label(self.test_tab, text="", font=("Segoe UI", 12, "bold"))
        self.q_label.pack(pady=5)

        self.a_label = tk.Label(self.test_tab, text="", wraplength=700, justify="left", fg="green")
        self.a_label.pack(pady=5)

        self.u_label = tk.Label(self.test_tab, text="", wraplength=700, justify="left", fg="blue")
        self.u_label.pack(pady=5)

        tk.Button(self.test_tab, text="Clear", command=self.clear_test,
                  bg="#922B21", fg="#F7DC6F", activebackground="#641E16", font=("Segoe UI", 10, "bold")).pack(pady=10)

    def refresh_dropdown(self):
        self.title_dropdown["values"] = [c["title"] for c in self.data]

    def start_test(self):
        selected = self.selected_title.get()
        for c in self.data:
            if c["title"] == selected:
                self.q_label.config(text=f"Question: {c['question']}")
                self.a_label.config(text=f"📘 Academic Explanation:\n{c['academic']}")
                self.u_label.config(text=f"🧠 Your Understanding:\n{c['understanding']}")
                return

    def clear_test(self):
        self.q_label.config(text="")
        self.a_label.config(text="")
        self.u_label.config(text="")

    # ---------- Analysis Tab ----------
    def create_analysis_tab(self):
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="Analysis")

        tk.Button(self.analysis_tab, text="Generate Chart", command=self.generate_chart,
                  bg="#7B241C", fg="#F7DC6F", activebackground="#922B21", font=("Segoe UI", 10, "bold")).pack(pady=10)

        self.chart_frame = ttk.Frame(self.analysis_tab)
        self.chart_frame.pack()

    def generate_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        tag_counts = {}
        for c in self.data:
            for tag in c["tags"].split(","):
                tag = tag.strip()
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.clear()
        ax.pie(tag_counts.values(), labels=tag_counts.keys(), autopct="%1.1f%%")
        ax.set_title("Concept Distribution by Tags")
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

# ---------- Launch App ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = ConceptCrafterApp(root)
    root.mainloop()
