import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from plyer import notification
from pynput import keyboard
from datetime import datetime
import json
import os

# --- Setup, Configuration & State ---
session_minutes = 0
next_break_threshold = 50  # Default 3-hour limit (change to e.g., 5-10 for testing)
stress_score = 0
stress_spikes_count = 0  # Tracks total stress spikes reaching threshold
backspace_burst = 0
session_start_time = datetime.now()
LOG_FILE = "crunchguard_log.json"

# --- Productivity Logging Function ---
def save_session_log(total_minutes, stress_count):
    today_date = datetime.now().strftime("%Y-%m-%d")
    log_entry = {
        "date": today_date,
        "active_minutes": total_minutes,
        "stress_spikes_detected": stress_count,
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
    print(f"\n[CrunchGuard] Session saved to {LOG_FILE}: {total_minutes} mins tracked, {stress_count} stress spikes.")

# --- Background Keystroke Listener (Stress Detection) ---
def on_press(key):
    global stress_score, backspace_burst
    try:
        if key == keyboard.Key.backspace:
            backspace_burst += 1
            if backspace_burst > 15:
                stress_score += 10
                backspace_burst = 0 
                print(f"[Stress Alert] Frustration spike progress! Current score: {stress_score}")
        else:
            backspace_burst = 0 
    except Exception:
        pass

# Start the global keyboard listener in a background daemon thread
listener = keyboard.Listener(on_press=on_press)
listener.daemon = True
listener.start()

# --- Interactive UI Prompts (Tkinter Break Manager) ---
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
        next_break_threshold = 50
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
print("CrunchGuard v1.1 Active: Monitoring background time, keystrokes & logging.")
print(f"Session started at: {session_start_time.strftime('%H:%M:%S')}")
print("=" * 50)

# --- Main Tracking Loop ---
try:
    while True:
        # NOTE: time.sleep(1) simulates 1 minute per second for rapid hackathon testing.
        # Change to time.sleep(60) for real-time tracking (1 tick = 1 real minute).
        time.sleep(1) 
        session_minutes += 1
        
        if session_minutes >= next_break_threshold:
            prompt_user_break()
        
        if stress_score >= 50:
            stress_spikes_count += 1  # Increment spike total properly
            notification.notify(
                title="CrunchGuard: Frustration Spike",
                message="Hammering the backspace? Step away for a 5-minute breather.",
                app_name="CrunchGuard",
                timeout=10
            )
            stress_score = 0  # Reset window for the next spike

except KeyboardInterrupt:
    save_session_log(session_minutes, stress_spikes_count)
    print("\n[CrunchGuard] Shutting down safely. Keep crushing your project!")
    