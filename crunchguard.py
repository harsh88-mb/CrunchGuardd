import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from plyer import notification
from pynput import keyboard

# --- Setup & Thresholds ---
session_minutes = 0
next_break_threshold = 180 # Initial 3-hour limit
stress_score = 0
backspace_burst = 0

# --- Phase 2: Keyboard Listener ---
def on_press(key):
    global stress_score, backspace_burst
    try:
        if key == keyboard.Key.backspace:
            backspace_burst += 1
            if backspace_burst > 15:
                stress_score += 10
                backspace_burst = 0 
                print(f"Stress spike! Score: {stress_score}")
        else:
            backspace_burst = 0 
    except Exception:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

# --- Phase 3: Interactive UI Prompts ---
def prompt_user_break():
    global session_minutes, next_break_threshold
    
    # Initialize hidden main window to ensure pop-ups render correctly
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True) 

    # Option 1 & 2: Stop or Continue
    wants_to_stop = messagebox.askyesno(
        "CrunchGuard: Strain Alert", 
        "You've been coding continuously for a long time. Ready to stop and take a break?",
        parent=root
    )
    
    if wants_to_stop:
        session_minutes = 0
        next_break_threshold = 180
    else:
        # Custom Timer Input
        snooze_time = simpledialog.askinteger(
            "CrunchGuard: Custom Reminder", 
            "In how many minutes should I remind you again?", 
            initialvalue=60,
            parent=root,
            minvalue=1,
            maxvalue=300
        )
        
        if snooze_time is None:
            snooze_time = 60 # Failsafe if they simply close the window
            
        next_break_threshold = session_minutes + snooze_time

    root.destroy()

print("CrunchGuard Active: Monitoring background time and keystrokes.")

# --- Phase 1: Main Tracking Loop ---
while True:
    # IMPORTANT: time.sleep(1) simulates 1 minute per second for fast testing.
    # Change to time.sleep(60) when you are ready to use this normally.
    time.sleep(1) 
    session_minutes += 1
    
    # Check if user has hit the 180-minute (or custom snooze) mark
    if session_minutes >= next_break_threshold:
        prompt_user_break()
    
    # Check if user is typing aggressively
    if stress_score >= 50:
        notification.notify(
            title="CrunchGuard: Frustration Spike",
            message="Hammering the backspace? Step away for 5 minutes.",
            app_name="CrunchGuard",
            timeout=10
        )
        stress_score = 0