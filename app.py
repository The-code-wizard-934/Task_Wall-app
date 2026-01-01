import customtkinter as ctk
from tkinter import messagebox
import engine
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModernTodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ZenPoint Dashboard")
        self.geometry("900x600")
        
        self.tasks = engine.load_tasks()
        # Ensure all tasks have a status field
        for task in self.tasks:
            if "status" not in task:
                task["status"] = "Pending"
        self.setup_ui()
        self.refresh_display()
        self.auto_sync()

    def setup_ui(self):
        # Grid Layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar for Inputs
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="NEW TASK", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        self.ent_name = ctk.CTkEntry(self.sidebar, placeholder_text="Task Name...", width=250)
        self.ent_name.pack(pady=10)
        
        self.ent_time = ctk.CTkEntry(self.sidebar, placeholder_text="Start Time (e.g. 09:00)", width=250)
        self.ent_time.pack(pady=10)
        
        self.ent_dur = ctk.CTkEntry(self.sidebar, placeholder_text="Duration (mins)", width=250)
        self.ent_dur.pack(pady=10)

        self.btn_add = ctk.CTkButton(self.sidebar, text="Add to Schedule", command=self.add_task)
        self.btn_add.pack(pady=20)

        # Main Content Area
        self.main_view = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.task_list_frame = ctk.CTkScrollableFrame(self.main_view, label_text="Today's Timeline")
        self.task_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Control Bar
        self.controls = ctk.CTkFrame(self.main_view, height=50)
        self.controls.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(self.controls, text="SYNC NOW", fg_color="#2ecc71", hover_color="#27ae60", command=self.sync).pack(side="right", padx=10)
        ctk.CTkButton(self.controls, text="CLEAR ALL", fg_color="#e74c3c", hover_color="#c0392b", command=self.clear_all).pack(side="left", padx=10)

    def add_task(self):
        task = {
            "name": self.ent_name.get(),
            "time": self.ent_time.get(),
            "duration": self.ent_dur.get(),
            "status": "Pending"
        }
        self.tasks.append(task)
        self.save_and_refresh()

    def toggle_status(self, index):
        statuses = ["Pending", "In Progress", "Done"]
        current = self.tasks[index].get("status", "Pending")
        next_status = statuses[(statuses.index(current) + 1) % len(statuses)]
        self.tasks[index]["status"] = next_status
        self.save_and_refresh()

    def save_and_refresh(self):
        engine.save_tasks(self.tasks)
        self.refresh_display()

    def refresh_display(self):
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
            
        for i, task in enumerate(self.tasks):
            frame = ctk.CTkFrame(self.task_list_frame)
            frame.pack(fill="x", pady=5, padx=5)
            
            status = task.get("status", "Pending")
            color = "#f1c40f" if status == "In Progress" else "#95a5a6"
            if status == "Done": color = "#2ecc71"

            ctk.CTkLabel(frame, text=f"{task['time']}", width=60).pack(side="left", padx=10)
            ctk.CTkLabel(frame, text=f"{task['name']}", anchor="w").pack(side="left", expand=True, fill="x")
            
            ctk.CTkButton(frame, text=status, width=100, fg_color=color, 
                          command=lambda idx=i: self.toggle_status(idx)).pack(side="right", padx=10)

    def sync(self):
        engine.update_wallpaper_image(self.tasks)
        
    def auto_sync(self):
        self.sync()
        self.after(300000, self.auto_sync) # Auto-refresh every 5 mins

    def clear_all(self):
        self.tasks = []
        self.save_and_refresh()

if __name__ == "__main__":
    app = ModernTodoApp()
    app.mainloop()