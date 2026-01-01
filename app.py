import customtkinter as ctk
from tkinter import messagebox
import engine
import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ZenPointApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task_WALL app Dashboard")
        self.geometry("1200x700")
        
        self.tasks = engine.load_tasks()
        self.editing_index = None
        self.timer_running = False
        self.time_left = 0
        self.active_task_name = ""
        self.category_filter = "All"

        self.setup_ui()
        self.refresh_display()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_mode = ctk.CTkLabel(self.sidebar, text="ADD NEW TASK", font=("Segoe UI", 22, "bold"))
        self.lbl_mode.pack(pady=30)
        
        self.ent_name = ctk.CTkEntry(self.sidebar, placeholder_text="What needs to be done?", width=300, height=40)
        self.ent_name.pack(pady=10)
        self.ent_time = ctk.CTkEntry(self.sidebar, placeholder_text="Time (e.g., 09:00)", width=300, height=40)
        self.ent_time.pack(pady=10)
        self.ent_dur = ctk.CTkEntry(self.sidebar, placeholder_text="Duration (minutes)", width=300, height=40)
        self.ent_dur.pack(pady=10)
        
        # New fields
        self.ent_due_date = ctk.CTkEntry(self.sidebar, placeholder_text="Due Date (YYYY-MM-DD HH:MM)", width=300, height=40)
        self.ent_due_date.pack(pady=10)
        self.opt_priority = ctk.CTkOptionMenu(self.sidebar, values=["Low", "Medium", "High"], width=300, height=40)
        self.opt_priority.pack(pady=10)
        self.opt_category = ctk.CTkOptionMenu(self.sidebar, values=["Work", "Personal", "Urgent", "Other"], width=300, height=40)
        self.opt_category.pack(pady=10)
        self.opt_recurring = ctk.CTkOptionMenu(self.sidebar, values=["None", "Daily", "Weekly"], width=300, height=40)
        self.opt_recurring.pack(pady=10)

        self.btn_save = ctk.CTkButton(self.sidebar, text="Save to Wallpaper", height=45, command=self.save_task)
        self.btn_save.pack(pady=20)

        # --- Timer Widget ---
        self.timer_card = ctk.CTkFrame(self.sidebar, fg_color="#2c3e50", corner_radius=10)
        self.timer_card.pack(fill="x", padx=20, pady=20)
        self.lbl_clock = ctk.CTkLabel(self.timer_card, text="00:00", font=("Consolas", 35, "bold"))
        self.lbl_clock.pack(pady=10)
        self.btn_timer = ctk.CTkButton(self.timer_card, text="Start Focus Mode", fg_color="#e67e22", hover_color="#d35400", command=self.toggle_timer)
        self.btn_timer.pack(pady=10)

        # --- Main View ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Filter buttons
        self.filter_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.filter_frame.pack(fill="x", pady=10)
        ctk.CTkButton(self.filter_frame, text="All", command=lambda: self.set_filter("All")).pack(side="left", padx=5)
        ctk.CTkButton(self.filter_frame, text="Work", command=lambda: self.set_filter("Work")).pack(side="left", padx=5)
        ctk.CTkButton(self.filter_frame, text="Personal", command=lambda: self.set_filter("Personal")).pack(side="left", padx=5)
        ctk.CTkButton(self.filter_frame, text="Urgent", command=lambda: self.set_filter("Urgent")).pack(side="left", padx=5)
        ctk.CTkButton(self.filter_frame, text="Other", command=lambda: self.set_filter("Other")).pack(side="left", padx=5)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_container, label_text="Your Daily Timeline", label_font=("Segoe UI", 16))
        self.scroll_frame.pack(fill="both", expand=True)

    def save_task(self):
        name, t_val, dur, due_date, priority, category, recurring = (
            self.ent_name.get(), self.ent_time.get(), self.ent_dur.get(),
            self.ent_due_date.get(), self.opt_priority.get(), self.opt_category.get(), self.opt_recurring.get()
        )
        if not (name and t_val and dur):
            messagebox.showwarning("Input Error", "Name, Time, and Duration are required!")
            return

        new_data = {
            "name": name, "time": t_val, "duration": dur, "status": "Pending",
            "due_date": due_date or None, "priority": priority, "category": category, "recurring": recurring
        }
        
        if self.editing_index is not None:
            self.tasks[self.editing_index] = new_data
            self.editing_index = None
            self.lbl_mode.configure(text="ADD NEW TASK")
        else:
            self.tasks.append(new_data)
            
        self.finalize_all()
        self.clear_inputs()

    def edit_task(self, index):
        self.editing_index = index
        task = self.tasks[index]
        self.ent_name.delete(0, 'end'); self.ent_name.insert(0, task['name'])
        self.ent_time.delete(0, 'end'); self.ent_time.insert(0, task['time'])
        self.ent_dur.delete(0, 'end'); self.ent_dur.insert(0, task['duration'])
        self.ent_due_date.delete(0, 'end'); self.ent_due_date.insert(0, task.get('due_date', ''))
        self.opt_priority.set(task.get('priority', 'Low'))
        self.opt_category.set(task.get('category', 'Other'))
        self.opt_recurring.set(task.get('recurring', 'None'))
        self.lbl_mode.configure(text="EDIT TASK")

    def toggle_timer(self):
        if not self.timer_running:
            # Find the first non-done task
            target = next((t for t in self.tasks if t['status'] != "Done"), None)
            if target:
                self.active_task_name = target['name']
                self.time_left = int(target['duration']) * 60
                self.timer_running = True
                self.btn_timer.configure(text="Stop Focus", fg_color="#c0392b")
                self.timer_tick()
        else:
            self.timer_running = False
            self.btn_timer.configure(text="Start Focus Mode", fg_color="#e67e22")

    def timer_tick(self):
        if self.timer_running and self.time_left > 0:
            m, s = divmod(self.time_left, 60)
            time_str = f"{m:02d}:{s:02d}"
            self.lbl_clock.configure(text=time_str)
            
            # Update wallpaper every 30 seconds during timer
            if self.time_left % 30 == 0:
                engine.update_wallpaper_image(self.tasks, {"name": self.active_task_name, "time_left": time_str})
            
            self.time_left -= 1
            self.after(1000, self.timer_tick)
        elif self.time_left <= 0:
            self.timer_running = False
            self.btn_timer.configure(text="Focus Done!", fg_color="#2ecc71")
            engine.update_wallpaper_image(self.tasks)

    def refresh_display(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        # Sort by time before showing
        self.tasks = sorted(self.tasks, key=lambda x: x.get('time', '00:00'))
        
        filtered_tasks = [task for task in self.tasks if self.category_filter == "All" or task.get('category') == self.category_filter]
        
        for i, task in enumerate(filtered_tasks):
            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=4, padx=5)
            
            # Color based on status and priority
            if task['status'] == "Done":
                color = "#2ecc71"
            elif task.get('priority') == "High":
                color = "#e74c3c"
            elif task.get('priority') == "Medium":
                color = "#f39c12"
            else:
                color = "#ffffff"
            
            # Check overdue
            overdue = False
            if task.get('due_date'):
                try:
                    due = datetime.datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M")
                    if due < datetime.datetime.now():
                        overdue = True
                        color = "#c0392b"  # Red for overdue
                except:
                    pass
            
            time_text = f"{task['time']}"
            if overdue:
                time_text += " (OVERDUE)"
            
            ctk.CTkLabel(row, text=time_text, width=120, font=("Arial", 14, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"[{task.get('category', 'Other')}] {task['name']}", anchor="w", text_color=color).pack(side="left", expand=True, fill="x")
            
            ctk.CTkButton(row, text="Edit", width=60, fg_color="#34495e", command=lambda idx=self.tasks.index(task): self.edit_task(idx)).pack(side="left", padx=5)
            
            status_btn_txt = "Done" if task['status'] != "Done" else "Reset"
            ctk.CTkButton(row, text=status_btn_txt, width=60, 
                          fg_color="#16a085" if task['status'] != "Done" else "#7f8c8d",
                          command=lambda idx=i: self.toggle_done(idx)).pack(side="left", padx=5)
            
            ctk.CTkButton(row, text="X", width=30, fg_color="#c0392b", command=lambda idx=i: self.delete_task(idx)).pack(side="left", padx=5)

    def toggle_done(self, index):
        self.tasks[index]["status"] = "Done" if self.tasks[index]["status"] != "Done" else "Pending"
        self.finalize_all()

    def delete_task(self, index):
        self.tasks.pop(index)
        self.finalize_all()

    def finalize_all(self):
        engine.save_tasks(self.tasks)
        self.refresh_display()
        engine.update_wallpaper_image(self.tasks)

    def clear_inputs(self):
        self.ent_name.delete(0, 'end'); self.ent_time.delete(0, 'end'); self.ent_dur.delete(0, 'end')
        self.ent_due_date.delete(0, 'end')
        self.opt_priority.set("Low")
        self.opt_category.set("Other")
        self.opt_recurring.set("None")

    def set_filter(self, category):
        self.category_filter = category
        self.refresh_display()

if __name__ == "__main__":
    app = ZenPointApp()
    app.mainloop()