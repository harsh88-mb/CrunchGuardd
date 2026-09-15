# CrunchGuard 🛡️⏱️

CrunchGuard is an intelligent productivity monitoring and break-management tool built specifically for hackathons and intense coding marathons. It tracks session duration, detects developer frustration in real-time, monitors active code editors, and enforces healthy break reminders.

## 🚀 Key Features

* **Smart Break Management:** Automatically prompts developers to rest after prolonged coding sessions with custom snooze options via a foreground-forced Tkinter GUI.
* **Frustration Detection:** Monitors background keystroke patterns (like rapid backspace bursts) to flag stress spikes and trigger breather alerts.
* **Active IDE Tracking:** Uses `psutil` to verify if your code editor (e.g., VS Code, PyCharm) is active during sessions.
* **Productivity Logging:** Automatically dumps session stats, active minutes, and frustration counts into a structured `crunchguard_log.json` file upon exit.

## 🛠️ Tech Stack

* **Python** (Core Logic)
* **Tkinter** (Interactive GUI & Prompts)
* **Pynput** (Background Keystroke Monitoring)
* **Plyer** (Desktop Notifications)
* **Psutil** (Process & IDE Tracking)
* **JSON** (Local Session Logging)

## ⚙️ Installation & Usage

1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name
