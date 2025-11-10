import logging
import socket
import json
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class QRadarLogger:
    def __init__(self):
        self.host = os.getenv('QRADAR_HOST')
        self.port = int(os.getenv('QRADAR_PORT', 514))
        self.protocol = os.getenv('QRADAR_PROTOCOL', 'TCP').upper()
        self.logger = self._setup_logger()
        self.sock = None
        if self.protocol == 'TCP':
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
    
    def _setup_logger(self):
        logger = logging.getLogger('QRadarLogger')
        logger.setLevel(logging.INFO)
        
        # File handler for local logging
        fh = logging.FileHandler('qradar_events.log')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _format_syslog_message(self, event_type, details):
        """Format message according to QRadar syslog format"""
        timestamp = datetime.utcnow().strftime('%b %d %H:%M:%S')
        hostname = socket.gethostname()
        
        # Convert details to JSON string if it's a dict
        if isinstance(details, dict):
            details = json.dumps(details)
        
        return f'<134>{timestamp} {hostname} WebApp: type="{event_type}" details="{details}"'
    
    def send_event(self, event_type, details):
        """Send event to QRadar via syslog"""
        try:
            message = self._format_syslog_message(event_type, details)
            
            if self.protocol == 'TCP':
                self.sock.send(f"{message}\n".encode('utf-8'))
            else:  # UDP
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(message.encode('utf-8'), (self.host, self.port))
                sock.close()
            
            self.logger.info(f"Event sent to QRadar: {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send event to QRadar: {str(e)}")
            return False
    
    def log_login_attempt(self, username, ip_address, success, details=None):
        """Log login attempts"""
        event_data = {
            "event_type": "LOGIN_ATTEMPT",
            "username": username,
            "ip_address": ip_address,
            "status": "success" if success else "failure",
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        return self.send_event("LOGIN_ATTEMPT", event_data)
    
    def log_admin_access(self, username, ip_address, resource, success, details=None):
        """Log admin access attempts"""
        event_data = {
            "event_type": "ADMIN_ACCESS",
            "username": username,
            "ip_address": ip_address,
            "resource": resource,
            "status": "success" if success else "failure",
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        return self.send_event("ADMIN_ACCESS", event_data)
    
    def log_suspicious_activity(self, username, ip_address, activity_type, details=None):
        """Log suspicious activities"""
        event_data = {
            "event_type": "SUSPICIOUS_ACTIVITY",
            "username": username,
            "ip_address": ip_address,
            "activity_type": activity_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        return self.send_event("SUSPICIOUS_ACTIVITY", event_data)
    
    def __del__(self):
        """Cleanup socket connection"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass

# Global instance
qradar_logger = QRadarLogger()