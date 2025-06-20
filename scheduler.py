import os
import schedule
import time
import subprocess
from datetime import datetime
import json

def run_scan(domain):
    LOCK_FILE = 'scan.lock'
    if os.path.exists(LOCK_FILE):
        print(f"[SCHEDULER] Scan already in progress. Skipping scheduled scan for {domain}.")
        return
    try:
        open(LOCK_FILE, 'w').close()
        print(f"[SCHEDULER] Triggering scan for domain: {domain} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        subprocess.run(["python3", "main.py", domain])
    finally:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

def main():
    config_path = 'schedule_config.json'
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        domain = config.get('domain', 'test')
        schedule_time = config.get('time', '15:00')
        frequency = config.get('frequency', 'daily')
    else:
        domain = os.getenv('SCHEDULE_DOMAIN', 'test')
        schedule_time = os.getenv('SCHEDULE_TIME', '15:00')
        frequency = os.getenv('SCHEDULE_FREQUENCY', 'daily')
    print(f"[SCHEDULER] Will run scan for domain '{domain}' {frequency} at {schedule_time}")
    if frequency == 'daily':
        schedule.every().day.at(schedule_time).do(run_scan, domain=domain)
    elif frequency == 'weekly':
        schedule.every().monday.at(schedule_time).do(run_scan, domain=domain)
    elif frequency == 'monthly':
        schedule.every(30).days.at(schedule_time).do(run_scan, domain=domain)
    else:
        schedule.every().day.at(schedule_time).do(run_scan, domain=domain)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
