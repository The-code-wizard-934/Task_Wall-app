import json, ctypes, os, datetime
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_IMAGE = os.path.join(BASE_DIR, "template.jpg")
OUTPUT_IMAGE = os.path.join(BASE_DIR, "current_wallpaper.jpg")
DATA_FILE = os.path.join(BASE_DIR, "tasks.json")

def load_tasks():
    try:
        with open(DATA_FILE, "r") as f:
            tasks = json.load(f)
            return sorted(tasks, key=lambda x: x.get('time', '00:00'))
    except: return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def update_wallpaper_image(tasks, active_timer=None):
    try:
        if not os.path.exists(TEMPLATE_IMAGE): return False
        
        # 1. Image Setup
        base = Image.open(TEMPLATE_IMAGE).convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        width, height = base.size
        
        # 2. Modern Color Palette
        COLOR_ACCENT = (255, 204, 0, 255)  # Vibrant Yellow-Gold
        COLOR_TEXT = (255, 255, 255, 255)  # Pure White
        COLOR_DIM = (255, 255, 255, 100)   # Faded White (Alpha)
        COLOR_PANE = (0, 0, 0, 140)        # Glassmorphism Pane
        COLOR_TIMER = (255, 59, 48, 255)   # iOS Red for urgency

        try:
            # Using bold variants if available makes it look much more professional
            f_header = ImageFont.truetype("arialbd.ttf", 32) 
            f_body = ImageFont.truetype("arial.ttf", 28)
            f_small = ImageFont.truetype("arial.ttf", 25)
        except:
            f_header = f_body = f_small = ImageFont.load_default()

        # 3. Draw Glassmorphism Pane (Background for the table)
        # Coordinates: [left, top, right, bottom]
        pane_x0, pane_y0, pane_x1 = 100, 100, 1300
        pane_y1 = min(150 + (len(tasks) + 1) * 75, height - 100)
        draw.rounded_rectangle([pane_x0, pane_y0, pane_x1, pane_y1], radius=30, fill=COLOR_PANE)

        # 4. Active Timer (Floating Badge style)
        if active_timer:
            timer_txt = f" {active_timer['name'].upper()} • {active_timer['time_left']} "
            t_w = draw.textlength(timer_txt, font=f_body)
            # Red glow effect
            draw.rounded_rectangle([width - t_w - 120, 50, width - 60, 120], radius=15, fill=COLOR_TIMER)
            draw.text((width - t_w - 90, 65), timer_txt, font=f_body, fill=COLOR_TEXT)

        # 5. Table Layout
        x_time, x_name, x_dur, x_status = 150, 320, 880, 1100
        y = 160
        
        # Headers with high tracking (spacing)
        draw.text((x_time, y), "TIME", font=f_header, fill=COLOR_ACCENT)
        draw.text((x_name, y), "TASK", font=f_header, fill=COLOR_ACCENT)
        draw.text((x_dur, y), "DURATION", font=f_header, fill=COLOR_ACCENT)
        draw.text((x_status, y), "STATUS", font=f_header, fill=COLOR_ACCENT)
        
        y += 85
        draw.line([(x_time, y-15), (x_status+150, y-15)], fill=COLOR_DIM, width=2)

        # 6. Task Rows
        sorted_tasks = sorted(tasks, key=lambda x: x.get('time', '00:00'))
        for task in sorted_tasks:
            status = task.get("status", "Pending")
            text_color = COLOR_DIM if status == "Done" else COLOR_TEXT
            
            # Use symbols for a cleaner look
            icon = "●" if status == "In Progress" else "○"
            if status == "Done": icon = "✓"

            draw.text((x_time, y), task.get('time', '--:--'), font=f_body, fill=text_color)
            draw.text((x_name, y), f"{icon}  {task.get('name', '')}", font=f_body, fill=text_color)
            draw.text((x_dur, y), f"{task.get('duration', '0')}m", font=f_body, fill=text_color)
            
            # Status badge
            status_txt = status.upper()
            draw.text((x_status, y), status_txt, font=f_body, fill=COLOR_ACCENT if status != "Done" else COLOR_DIM)
            
            y += 65 # Compact but readable spacing

        # 7. Metadata
        sync_time = datetime.datetime.now().strftime("%I:%M %p")
        draw.text((width - 300, height - 60), f"SYSTEM SYNCED: {sync_time}", font=f_small, fill=COLOR_DIM)

        # 8. Merge and Apply
        out_img = Image.alpha_composite(base, overlay).convert("RGB")
        out_img.save(OUTPUT_IMAGE, quality=100)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(OUTPUT_IMAGE), 3)
        return True
    except Exception as e:
        print(f"Engine Error: {e}")
        return False