# 🚀 Task_Wall-app

**Task_Wall-app** is a sophisticated Windows productivity tool that bridges the gap between your to-do list and your workspace. It transforms your desktop wallpaper into a high-end, live **"Heads-Up Display" (HUD)** using glassmorphism aesthetics, ensuring your daily goals are always in your line of sight.

---

## ✨ Key Features

- **Glassmorphism HUD**  
  Tasks are rendered onto a semi-transparent, rounded "glass" pane to ensure readability against any background image.

- **Live Focus Timer**  
  A dedicated *"Dynamic Island"* style countdown badge appears on your wallpaper to keep you focused on the current task.

- **Real-Time Sync**  
  Any changes made in the Dashboard (Adding, Editing, or Marking Done) are instantly stamped onto the wallpaper.

- **Smart Auto-Sorting**  
  The application automatically reorders tasks based on their scheduled time slots (`HH:MM`).

- **Visual Hierarchy**  
  Uses professional symbols (`●` for Active, `○` for Pending, `✓` for Done) and color-coding to provide instant status context.

- **Metadata Tracking**  
  Includes a **"Last System Sync"** timestamp on the wallpaper to verify data freshness.

---

## 🛠️ How it Works

The application operates as a three-part system:

1. **The Management UI**  
   A modern Dark Mode dashboard built with **CustomTkinter** where you input and manage your schedule.

2. **The Rendering Engine**  
   A Python logic layer using the **Pillow** library that takes your `template.jpg` and layers your task data over it.

3. **The OS Injector**  
   A system-level bridge that uses the Windows `SystemParametersInfoW` API to force-refresh the desktop background with the newly generated image.

---

## 🎯 Use Cases

- **Deep Work Sessions**  
  Keep a countdown of your current sprint visible even when all app windows are minimized.

- **Daily Routine Management**  
  For users who struggle with *"out of sight, out of mind"*—your schedule becomes part of your environment.

- **Minimalist Productivity**  
  Eliminates the need to keep a heavy project management app open on a second monitor.

- **Public Dashboards**  
  Can be used on shared office displays to show the daily agenda or *"Station Updates."*

---

## 📥 Installation & Setup

### 1. Prerequisites

- Windows OS (Required for wallpaper API calls)
- Python **3.8+**

### 2. Required Libraries

Install the necessary dependencies via terminal:

```bash
pip install Pillow customtkinter
```

## 3. File Directory Structure

Ensure your project folder is organized as follows:
```
Task_Wall-app/
├── Task_Wall-app.py      # The Dashboard UI
├── engine.py             # The Rendering Engine
├── template.jpg          # YOUR high-res background image
├── arial.ttf             # Font file (Copy from C:\Windows\Fonts)
└── tasks.json            # (Auto-generated) Data storage
```

## 📦 How to Create an Executable (.exe)

To bundle this project into a standalone app that runs without needing Python installed, follow these steps:

### Install PyInstaller
```
pip install pyinstaller
```

### Run the Build Command
```
pyinstaller --noconsole --onefile --name "Task_Wall-app" --collect-all customtkinter app.py
```

## Post-Build Setup

1. Navigate to the newly created dist folder.
2. Move Task_Wall-app.exe out of dist and into your main project folder  
   (where template.jpg and arial.ttf are located).
3. Run the .exe to start using your app.


## ⚠️ Important Notes

### Resolution
For the best look, ensure your template.jpg matches your monitor's aspect ratio  
(e.g., 1920x1080).

### Font
The app looks for arial.ttf and arialbd.ttf (bold) in the local directory for the best rendering quality.


The app looks for arial.ttf and arialbd.ttf (bold) in the local directory for the best rendering quality.
