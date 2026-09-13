import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from plyer import notification
from pynput import keyboard
from datetime import datetime
import json
import os
import psutil

# --- Setup, Configuration & State ---
session_minutes = 0
next_break_threshold = 90 # Change to 5 for quick testinggit 
stress_score = 0
backspace_burst = 0
session_start_time = datetime.now()
LOG_FILE = "crunchguard_log.json"

# --- Active IDE Detection ---
def check_active_ide():
    ide_processes = ["code.exe", "pycharm64.exe", "devenv.exe", "sublime_text.exe", "code"]
    detected_ides = []
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name and name.lower() in [ide.lower() for ide in ide_processes]:
                if name not in detected_ides:
                    detected_ides.append(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return detected_ides

# --- Productivity Logging Function ---
def save_session_log(total_minutes, stress_count):
    today_date = datetime.now().strftime("%Y-%m-%d")
    active_ides = check_active_ide()
    log_entry = {
        "date": today_date,
        "active_minutes": total_minutes,
        "stress_spikes_detected": stress_count,
        "detected_ides": active_ides,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    
    data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
            
    data.append(log_entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\n[CrunchGuard] Session saved to {LOG_FILE}: {total_minutes} mins tracked. IDEs: {active_ides}")

# --- Background Keystroke Listener ---
def on_press(key):
    global stress_score, backspace_burst
    try:
        if key == keyboard.Key.backspace:
            backspace_burst += 1
            if backspace_burst > 15:
                stress_score += 10
                backspace_burst = 0 
                print(f"[Stress Alert] Frustration spike detected! Score: {stress_score}")
        else:
            backspace_burst = 0 
    except Exception:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.daemon = True
listener.start()

# --- Interactive UI Prompts ---
def prompt_user_break():
    global session_minutes, next_break_threshold
    
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True) 

    wants_to_stop = messagebox.askyesno(
        "CrunchGuard: Strain Alert", 
        "You've been coding continuously for a long time. Ready to stop and take a break?",
        parent=root
    )
    
    if wants_to_stop:
        session_minutes = 0
        next_break_threshold = 90
        notification.notify(
            title="CrunchGuard: Break Started",
            message="Great job! Step away from the screen and stretch.",
            app_name="CrunchGuard",
            timeout=5
        )
    else:
        snooze_time = simpledialog.askinteger(
            "CrunchGuard: Custom Reminder", 
            "In how many minutes should I remind you again?", 
            initialvalue=60,
            parent=root,
            minvalue=1,
            maxvalue=300
        )
        
        if snooze_time is None:
            snooze_time = 60  
            
        next_break_threshold = session_minutes + snooze_time
        print(f"[CrunchGuard] Snoozed for {snooze_time} minutes.")

    root.destroy()

print("=" * 50)
print("CrunchGuard v1.2 Active: Monitoring time, keystrokes & IDE tracking.")
print(f"Session started at: {session_start_time.strftime('%H:%M:%S')}")
print("=" * 50)

# --- Main Tracking Loop ---
try:
    while True:
        time.sleep(1) 
        session_minutes += 1
        
        if session_minutes >= next_break_threshold:
            prompt_user_break()
        
        if stress_score >= 50:
            notification.notify(
                title="CrunchGuard: Frustration Spike",
                message="Hammering the backspace? Step away for a 5-minute breather.",
                app_name="CrunchGuard",
                timeout=10
            )
            stress_score = 0  

except KeyboardInterrupt:
    save_session_log(session_minutes, stress_score)
    print("\n[CrunchGuard] Shutting down safely. Keep crushing your project!")