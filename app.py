import customtkinter as ctk
from tkinter import messagebox
import engine

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ZenPointApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task_WALL app Dashboard")
        self.geometry("1100x700")
        
        self.tasks = engine.load_tasks()
        self.editing_index = None
        self.timer_running = False
        self.time_left = 0
        self.active_task_name = ""

        self.setup_ui()
        self.refresh_display()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_mode = ctk.CTkLabel(self.sidebar, text="ADD NEW TASK", font=("Segoe UI", 22, "bold"))
        self.lbl_mode.pack(pady=30)
        
        self.ent_name = ctk.CTkEntry(self.sidebar, placeholder_text="What needs to be done?", width=260, height=40)
        self.ent_name.pack(pady=10)
        self.ent_time = ctk.CTkEntry(self.sidebar, placeholder_text="Time (e.g., 09:00)", width=260, height=40)
        self.ent_time.pack(pady=10)
        self.ent_dur = ctk.CTkEntry(self.sidebar, placeholder_text="Duration (minutes)", width=260, height=40)
        self.ent_dur.pack(pady=10)

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
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_container, label_text="Your Daily Timeline", label_font=("Segoe UI", 16))
        self.scroll_frame.pack(fill="both", expand=True)

    def save_task(self):
        name, t_val, dur = self.ent_name.get(), self.ent_time.get(), self.ent_dur.get()
        if not (name and t_val and dur):
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        new_data = {"name": name, "time": t_val, "duration": dur, "status": "Pending"}
        
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
        
        for i, task in enumerate(self.tasks):
            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=4, padx=5)
            
            color = "#2ecc71" if task['status'] == "Done" else "#ffffff"
            ctk.CTkLabel(row, text=f"{task['time']}", width=70, font=("Arial", 14, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=task['name'], anchor="w", text_color=color).pack(side="left", expand=True, fill="x")
            
            ctk.CTkButton(row, text="Edit", width=60, fg_color="#34495e", command=lambda idx=i: self.edit_task(idx)).pack(side="left", padx=5)
            
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

if __name__ == "__main__":
    app = ZenPointApp()
    app.mainloop()