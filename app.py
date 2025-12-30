import tkinter as tk
from tkinter import messagebox, ttk
import engine

class WallpaperTaskApp:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("Wallpaper Task Manager")
            self.root.geometry("500x600")
            
            print("Loading tasks...")
            self.tasks = engine.load_tasks()
            print(f"Loaded {len(self.tasks)} tasks")
            
            print("Setting up UI...")
            self.setup_ui()
            self.refresh_listbox()
            print("Application initialized successfully!")
        except Exception as e:
            import traceback
            print(f"Error initializing application: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise

    def setup_ui(self):
        # Input Section
        frame = tk.Frame(self.root, pady=20)
        frame.pack()

        tk.Label(frame, text="Task Name:").grid(row=0, column=0)
        self.ent_name = tk.Entry(frame, width=30)
        self.ent_name.grid(row=0, column=1)

        tk.Label(frame, text="Duration (min):").grid(row=1, column=0)
        self.ent_dur = tk.Entry(frame, width=30)
        self.ent_dur.grid(row=1, column=1)

        tk.Label(frame, text="Time Slot:").grid(row=2, column=0)
        self.ent_time = tk.Entry(frame, width=30)
        self.ent_time.grid(row=2, column=1)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Task", command=self.handle_add, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Update Selected", command=self.handle_update).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove", command=self.handle_remove, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)

        # List Display
        self.tree = ttk.Treeview(self.root, columns=("Time", "Task", "Dur"), show='headings')
        self.tree.heading("Time", text="Time")
        self.tree.heading("Task", text="Task Name")
        self.tree.heading("Dur", text="Min")
        self.tree.column("Time", width=70)
        self.tree.column("Dur", width=50)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Button(self.root, text="SYNC TO WALLPAPER", command=self.handle_sync, height=2, bg="#2196F3", fg="white").pack(fill=tk.X, padx=20, pady=10)

    def refresh_listbox(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for task in self.tasks:
            self.tree.insert("", tk.END, values=(task['time'], task['name'], task['duration']))

    def handle_add(self):
        new_task = {"name": self.ent_name.get(), "duration": self.ent_dur.get(), "time": self.ent_time.get()}
        self.tasks.append(new_task)
        self.finalize_change()

    def handle_remove(self):
        selected = self.tree.selection()
        if selected:
            idx = self.tree.index(selected[0])
            self.tasks.pop(idx)
            self.finalize_change()

    def handle_update(self):
        selected = self.tree.selection()
        if selected:
            idx = self.tree.index(selected[0])
            self.tasks[idx] = {"name": self.ent_name.get(), "duration": self.ent_dur.get(), "time": self.ent_time.get()}
            self.finalize_change()

    def finalize_change(self):
        engine.save_tasks(self.tasks)
        self.refresh_listbox()

    def handle_sync(self):
        success = engine.update_wallpaper_image(self.tasks)
        if success:
            messagebox.showinfo("Success", "Wallpaper Updated!")

if __name__ == "__main__":
    try:
        print("Starting Wallpaper Task Manager...")
        root = tk.Tk()
        app = WallpaperTaskApp(root)
        print("Window created successfully. Starting main loop...")
        root.mainloop()
    except Exception as e:
        import traceback
        print(f"Error starting application: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        input("Press Enter to exit...")