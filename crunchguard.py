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
next_break_threshold = 180  # Default 3-hour limit (Change to 5 for demo)
stress_score = 0
backspace_burst = 0
cumulative_stress = 0  
total_stress_events = 0  # Permanent counter for accurate JSON logging
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
    print(f"\n[CrunchGuard] Session saved to {LOG_FILE}: {total_minutes} mins tracked, {stress_count} spikes logged.")

# --- Background Keystroke Listener (Stress Detection) ---
def on_press(key):
    global stress_score, backspace_burst, total_stress_events
    try:
        if key == keyboard.Key.backspace:
            backspace_burst += 1
            if backspace_burst > 15:  # Change to 3 for quick demo
                stress_score += 10    # Change to 50 for quick demo
                total_stress_events += 1  
                backspace_burst = 0 
                print(f"[Stress Alert] Frustration spike detected! Score: {stress_score}")
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
        next_break_threshold = 180
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

def show_critical_warning():
    """Displays a large, unignorable on-screen warning when cumulative stress is too high."""
    root = tk.Tk()
    root.title("CRITICAL STRAIN WARNING")
    root.attributes('-topmost', True)
    
    # Make it a large window centered on the screen
    window_width = 900
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
    
    root.configure(bg='#b30000')  # Deep red background

    msg = "You're working way too hard.\nGive your mind a rest and work later with fresh mind."
    label = tk.Label(root, text=msg, font=("Helvetica", 26, "bold"), bg='#b30000', fg='white')
    label.pack(expand=True, pady=40)
    
    def dismiss():
        root.destroy()
        
    btn = tk.Button(root, text="I Will Rest Now", font=("Helvetica", 18, "bold"), command=dismiss, padx=20, pady=10)
    btn.pack(pady=30)
    
    root.mainloop()

print("=" * 50)
print("CrunchGuard v1.3 Active: Monitoring background time, keystrokes & logging.")
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
            cumulative_stress += 25  # Change to 150 for quick demo
            print(f"[CrunchGuard] Cumulative stress increased to {cumulative_stress}/300.")
            
            if cumulative_stress >= 300:
                show_critical_warning()
                cumulative_stress = 0  # Reset after showing the big warning
            else:
                notification.notify(
                    title="CrunchGuard: Frustration Spike",
                    message="Hammering the backspace? Step away for a 5-minute breather.",
                    app_name="CrunchGuard",
                    timeout=10
                )
            
            stress_score = 0  # Reset local stress score after processing

except KeyboardInterrupt:
    save_session_log(session_minutes, total_stress_events)
    print("\n[CrunchGuard] Shutting down safely. Keep crushing your project!")