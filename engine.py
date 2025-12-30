import json
import ctypes
import os
from PIL import Image, ImageDraw, ImageFont

# Get the absolute path of the current folder to avoid "File Not Found" errors
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "tasks.json")
TEMPLATE_IMAGE = os.path.join(BASE_DIR, "template.jpg")
OUTPUT_IMAGE = os.path.join(BASE_DIR, "current_wallpaper.jpg")

def load_tasks():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def update_wallpaper_image(tasks):
    try:
        base = Image.open(TEMPLATE_IMAGE).convert("RGB")
        draw = ImageDraw.Draw(base)
        
        # 1. Font Setup (Use a slightly smaller font for the table)
        try:
            font_header = ImageFont.truetype("colonna.ttf", 40) # Bold-ish header
            font_row = ImageFont.truetype("arial.ttf", 30)    # Regular row
        except:
            font_header = ImageFont.load_default()
            font_row = ImageFont.load_default()

        # 2. Define Table Columns (X-Coordinates)
        col_time = 100
        col_task = 300
        col_dur = 800
        y_pos = 100 # Starting height

        # 3. Draw Table Headers
        draw.text((col_time, y_pos), "TIME", font=font_header, fill=(255, 255, 255))
        draw.text((col_task, y_pos), "Task Name", font=font_header, fill=(255, 255, 255))
        draw.text((col_dur, y_pos), "Time Slot", font=font_header, fill=(255, 255, 255))
        
        # Draw a simple separator line under headers
        draw.line([(col_time, y_pos+50), (col_dur+100, y_pos+50)], fill=(255, 255, 255), width=2)
        
        y_pos += 80 # Move down to start rows

        # 4. Draw Rows
        for task in tasks:
            name = str(task.get('name', ''))
            time = str(task.get('time', ''))
            dur = f"{task.get('duration', '')}m"

            draw.text((col_time, y_pos), time, font=font_row, fill=(200, 200, 200))
            draw.text((col_task, y_pos), name, font=font_row, fill=(255, 255, 255))
            draw.text((col_dur, y_pos), dur, font=font_row, fill=(200, 200, 200))
            
            y_pos += 50 # Space between rows

        # 5. Save and Apply
        base.save(OUTPUT_IMAGE, "JPEG", quality=100)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(OUTPUT_IMAGE), 3)
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False