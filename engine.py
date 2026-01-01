import json, ctypes, os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_IMAGE = os.path.join(BASE_DIR, "template.jpg")
OUTPUT_IMAGE = os.path.join(BASE_DIR, "current_wallpaper.jpg")

def load_tasks():
    try:
        with open("tasks.json", "r") as f: return json.load(f)
    except: return []

def save_tasks(tasks):
    with open("tasks.json", "w") as f: json.dump(tasks, f, indent=4)

def update_wallpaper_image(tasks):
    try:
        base = Image.open(TEMPLATE_IMAGE).convert("RGB")
        draw = ImageDraw.Draw(base)
        
        # UI Theme Colors
        COLOR_MAIN = (255, 255, 255)
        COLOR_DIM = (150, 150, 150)
        COLOR_ACCENT = (46, 204, 113) # Green for Done
        COLOR_ACTIVE = (241, 196, 15) # Yellow for Progress

        try:
            f_header = ImageFont.truetype("arial.ttf", 45)
            f_body = ImageFont.truetype("arial.ttf", 28)
        except:
            f_header = f_body = ImageFont.load_default()

        # Coordinates
        x_time, x_name, x_status = 150, 300, 850
        y = 150

        # Draw Header
        draw.text((x_time, y), "SCHEDULE", font=f_header, fill=COLOR_ACTIVE)
        draw.line([(x_time, y+60), (x_status+100, y+60)], fill=COLOR_MAIN, width=3)
        y += 100

        for task in tasks:
            status = task.get("status", "Pending")
            text_color = COLOR_MAIN
            prefix = "○"
            
            if status == "Done":
                text_color = COLOR_DIM
                prefix = "●"
            elif status == "In Progress":
                text_color = COLOR_ACTIVE
                prefix = "▶"

            # Draw Row
            draw.text((x_time, y), task['time'], font=f_body, fill=text_color)
            draw.text((x_name, y), f"{prefix} {task['name']}", font=f_body, fill=text_color)
            draw.text((x_status, y), status.upper(), font=f_body, fill=text_color)
            
            y += 55

        base.save(OUTPUT_IMAGE, quality=100)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(OUTPUT_IMAGE), 3)
    except Exception as e:
        print(f"Error: {e}")