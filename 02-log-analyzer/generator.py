import time
import random
import os

# Ensure the directory exists
RAW_DIR = "logs/raw"
if not os.path.exists(RAW_DIR):
    os.makedirs(RAW_DIR)

# Realistic attack patterns
ips = ["192.168.1.105", "10.0.0.42", "172.16.0.5", "45.33.22.11"]
users = ["root", "admin", "user1", "guest", "db_admin"]

def generate_fake_log():
    timestamp = time.strftime("%b %d %H:%M:%S")
    ip = random.choice(ips)
    user = random.choice(users)
    
    # 80% chance of a "Failed Login" (the threat we want to catch)
    if random.random() < 0.8:
        return f"{timestamp} my-server sshd[1234]: Failed password for {user} from {ip} port 54321 ssh2\n"
    else:
        return f"{timestamp} my-server sshd[1234]: Accepted password for {user} from {ip} port 54321 ssh2\n"

print("🚀 Starting Attack Simulator... Press Ctrl+C to stop.")

try:
    while True:
        # Create a new log file every few seconds to trigger the Java WatchService
        file_path = os.path.join(RAW_DIR, f"auth_{int(time.time())}.log")
        with open(file_path, "w") as f:
            for _ in range(5): # Write 5 lines per file
                f.write(generate_fake_log())
        
        print(f" [+] Generated new log batch: {file_path}")
        time.sleep(5) # Wait 5 seconds before the next "attack"
except KeyboardInterrupt:
    print("\nStopping simulator.")