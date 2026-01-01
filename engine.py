import json, ctypes, os, datetime, textwrap
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_IMAGE = os.path.join(BASE_DIR, "template.jpg")
OUTPUT_IMAGE = os.path.join(BASE_DIR, "current_wallpaper.jpg")
DATA_FILE = os.path.join(BASE_DIR, "tasks.json")

def load_tasks():
    try:
        with open(DATA_FILE, "r") as f:
            tasks = json.load(f)
    except:
        return []
    
    now = datetime.datetime.now()
    new_tasks = []
    for task in tasks:
        recurring = task.get('recurring', 'None')
        if recurring != 'None' and task.get('due_date'):
            try:
                due = datetime.datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M")
                if due < now:
                    # Generate new task
                    if recurring == 'Daily':
                        new_due = due + datetime.timedelta(days=1)
                    elif recurring == 'Weekly':
                        new_due = due + datetime.timedelta(weeks=1)
                    new_task = task.copy()
                    new_task['due_date'] = new_due.strftime("%Y-%m-%d %H:%M")
                    new_task['status'] = 'Pending'
                    new_tasks.append(new_task)
            except:
                pass
        new_tasks.append(task)
    
    # Save updated tasks
    with open(DATA_FILE, "w") as f:
        json.dump(new_tasks, f, indent=4)
    
    return sorted(new_tasks, key=lambda x: x.get('time', '00:00'))

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

        # Calculate pane height based on tasks
        sorted_tasks = sorted(tasks, key=lambda x: x.get('time', '00:00'))
        total_height = 150 + 85  # headers + line
        for task in sorted_tasks:
            name_text = f"[{task.get('category', 'Other')}] {'●' if task.get('status') == 'In Progress' else '○' if task.get('status') != 'Done' else '✓'}  {task.get('name', '')}"
            wrapped = textwrap.wrap(name_text, width=25)
            extra = max(0, len(wrapped) - 1) * 30
            total_height += 65 + extra

        # 3. Draw Glassmorphism Pane (Background for the table)
        # Coordinates: [left, top, right, bottom]
        pane_x0, pane_y0, pane_x1 = 100, 100, 1500
        pane_y1 = min(total_height, height - 100)
        draw.rounded_rectangle([pane_x0, pane_y0, pane_x1, pane_y1], radius=30, fill=COLOR_PANE)

        # 4. Active Timer (Floating Badge style)
        if active_timer:
            timer_txt = f" {active_timer['name'].upper()} • {active_timer['time_left']} "
            t_w = draw.textlength(timer_txt, font=f_body)
            # Red glow effect
            draw.rounded_rectangle([width - t_w - 120, 50, width - 60, 120], radius=15, fill=COLOR_TIMER)
            draw.text((width - t_w - 90, 65), timer_txt, font=f_body, fill=COLOR_TEXT)

        # 5. Table Layout
        x_time, x_name, x_dur, x_due, x_status = 150, 320, 780, 1050, 1250
        y = 160
        
        # Headers with high tracking (spacing)
        draw.text((x_time, y), "TIME", font=f_header, fill=COLOR_ACCENT)
        draw.text((x_name, y), "TASK", font=f_header, fill=COLOR_ACCENT)
        draw.text((x_dur, y), "DURATION", font=f_header, fill=COLOR_ACCENT)
        draw.text((x_due, y), "DUE DATE", font=f_header, fill=COLOR_ACCENT)
        draw.text((x_status, y), "STATUS", font=f_header, fill=COLOR_ACCENT)
        
        y += 85
        draw.line([(x_time, y-15), (x_status+150, y-15)], fill=COLOR_DIM, width=2)

        # 6. Task Rows
        for task in sorted_tasks:
            status = task.get("status", "Pending")
            priority = task.get("priority", "Low")
            category = task.get("category", "Other")
            
            # Color based on priority
            if status == "Done":
                text_color = COLOR_DIM
            elif priority == "High":
                text_color = (255, 59, 48, 255)  # Red
            elif priority == "Medium":
                text_color = (255, 204, 0, 255)  # Yellow
            else:
                text_color = COLOR_TEXT
            
            # Use symbols for a cleaner look
            icon = "●" if status == "In Progress" else "○"
            if status == "Done": icon = "✓"

            draw.text((x_time, y), task.get('time', '--:--'), font=f_body, fill=text_color)
            
            # Wrap name text
            name_text = f"[{category}] {icon}  {task.get('name', '')}"
            wrapped_name = textwrap.wrap(name_text, width=25)  # Approximate chars for column width
            for i, line in enumerate(wrapped_name[:2]):  # Limit to 2 lines
                draw.text((x_name, y + i * 30), line, font=f_body, fill=text_color)
            
            draw.text((x_dur, y), f"{task.get('duration', '0')}m", font=f_body, fill=text_color)
            draw.text((x_due, y), task.get('due_date', '--'), font=f_body, fill=text_color)
            
            # Status badge
            status_txt = status.upper()
            draw.text((x_status, y), status_txt, font=f_body, fill=COLOR_ACCENT if status != "Done" else COLOR_DIM)
            
            # Adjust y for wrapped lines
            extra_lines = max(0, len(wrapped_name) - 1)
            y += 65 + extra_lines * 30

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