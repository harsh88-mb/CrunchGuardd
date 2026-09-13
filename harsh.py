import time
from plyer import notification

# Configure your thresholds
session_minutes = 0
strain_threshold = 90  # Trigger an alert at 90 minutes

print("CrunchGuard is actively monitoring your session...")

while True:
    # We use 1 second to simulate 1 minute for rapid testing
    time.sleep(1) 
    session_minutes += 1
    
    print(f"Session active: {session_minutes} simulated minutes")

    if session_minutes >= strain_threshold:
        # Deploy the empathetic intervention
        notification.notify(
            title="CrunchGuard: Workload Strain Detected",
            message="You have been coding continuously for 90 minutes. It's time to step back and take a quick break.",
            app_name="CrunchGuard",
            timeout=10
        )
        print("Alert triggered. Resetting session timer...")
        session_minutes = 0 # Reset the timer after the break nudge