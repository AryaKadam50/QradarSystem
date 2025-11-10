"""
Simulate suspicious events for testing QRadar integration.
This script will:
 - Attempt repeated failed logins against the local API to create alerts
 - Send a direct QRadar syslog event via qradar_logger

Usage (after starting the server):
    python -m app.simulate_events

Make sure environment variables QRADAR_HOST/PORT are set in .env for syslog forwarding.
"""
import time
import requests
from .qradar_logger import qradar_logger

API = 'http://localhost:8000'


def repeated_failed_logins(username='nonexistent', attempts=10, interval=0.5):
    print(f"Sending {attempts} failed login attempts for '{username}' to {API}/auth/login")
    for i in range(attempts):
        try:
            r = requests.post(API + '/auth/login', data={'username': username, 'password': 'wrongpass', 'grant_type': 'password'}, timeout=5)
            print(i+1, r.status_code)
        except Exception as e:
            print('request error', e)
        time.sleep(interval)


def send_direct_syslog_example():
    print('Sending a direct suspicious syslog event to QRadar via qradar_logger')
    qradar_logger.log_suspicious_activity(username='attacker', ip_address='192.0.2.55', activity_type='port_scan', details={'ports': [22, 80, 443]})


if __name__ == '__main__':
    repeated_failed_logins(attempts=7)
    send_direct_syslog_example()
