from datetime import datetime

def log_session(victim_ip, command, output):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("sessions.log", "a") as f:
        f.write(f"[{now}] Victim: {victim_ip}\n")
        f.write(f">> {command}\n{output}\n{'-'*50}\n")
