import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from plyer import notification
from pynput import keyboard
from datetime import datetime

# --- Phase 0: Setup, Configuration & State ---
session_minutes = 0
next_break_threshold = 180  # Default 3-hour limit (change to e.g., 5-10 for testing)
stress_score = 0
backspace_burst = 0
session_start_time = datetime.now()

# --- Phase 2: Background Keystroke Listener (Stress Detection) ---
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

# Start the global keyboard listener in a background thread
listener = keyboard.Listener(on_press=on_press)
listener.daemon = True
listener.start()

# --- Phase 3: Interactive UI Prompts (Tkinter Break Manager) ---
def prompt_user_break():
    global session_minutes, next_break_threshold
    
    # Initialize a temporary, hidden root window for native system pop-ups
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True) 

    # Prompt 1: Check if user wants to take a break
    wants_to_stop = messagebox.askyesno(
        "CrunchGuard: Strain Alert", 
        "You've been coding continuously for a long time. Ready to stop and take a break?",
        parent=root
    )
    
    if wants_to_stop:
        session_minutes = 0
        next_break_threshold = 180
        notification.notify(
            title="CrunchGuard: Break Started",
            message="Great job! Step away from the screen and stretch.",
            app_name="CrunchGuard",
            timeout=5
        )
    else:
        # Prompt 2: Custom Snooze/Reminder Input
        snooze_time = simpledialog.askinteger(
            "CrunchGuard: Custom Reminder", 
            "In how many minutes should I remind you again?", 
            initialvalue=60,
            parent=root,
            minvalue=1,
            maxvalue=300
        )
        
        if snooze_time is None:
            snooze_time = 60  # Failsafe fallback if dialog is closed
            
        next_break_threshold = session_minutes + snooze_time
        print(f"[CrunchGuard] Snoozed for {snooze_time} minutes.")

    root.destroy()

print("=" * 50)
print("CrunchGuard v1.0 Active: Monitoring background time & keystrokes.")
print(f"Session started at: {session_start_time.strftime('%H:%M:%S')}")
print("=" * 50)

# --- Phase 1: Main Tracking Loop ---
try:
    while True:
        # NOTE: time.sleep(1) simulates 1 minute per second for rapid hackathon testing.
        # Change to time.sleep(60) for real-time tracking (1 tick = 1 real minute).
        time.sleep(1) 
        session_minutes += 1
        
        # Check if session duration has hit the break threshold
        if session_minutes >= next_break_threshold:
            prompt_user_break()
        
        # Check if cumulative typing frustration/stress has crossed the threshold
        if stress_score >= 50:
            notification.notify(
                title="CrunchGuard: Frustration Spike",
                message="Hammering the backspace? Step away for a 5-minute breather.",
                app_name="CrunchGuard",
                timeout=10
            )
            stress_score = 0  # Reset score after alert

except KeyboardInterrupt:
    print("\n[CrunchGuard] Shutting down safely. Keep crushing your project!")