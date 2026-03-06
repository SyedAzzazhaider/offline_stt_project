"""
Logger Module - Member 3
Provides timestamped logging functionality for STT sessions
"""
import json
import os
from datetime import datetime


class Logger:
    """Handles session logging with timestamps in JSON format"""
    
    def __init__(self, log_dir="./logs"):
        """
        Initialize logger with log directory
        
        Args:
            log_dir: Directory path for storing log files
        """
        self.log_dir = log_dir
        self.session_logs = []
        self.session_start_time = None
        
        # Create log directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def start_session(self):
        """Start a new logging session"""
        self.session_start_time = datetime.now()
        self.session_logs = []
        print(f"[Logger] Session started at {self.session_start_time.isoformat()}")
    
    def log_recognition(self, text, is_final=False):
        """
        Log a recognition result with timestamp
        
        Args:
            text: Recognized text
            is_final: Whether this is a final result
        """
        if not self.session_start_time:
            return
        
        timestamp = datetime.now()
        duration_ms = int((timestamp - self.session_start_time).total_seconds() * 1000)
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "recognized_text": text,
            "duration_ms": duration_ms,
            "is_final": is_final
        }
        
        self.session_logs.append(log_entry)
        print(f"[Logger] {timestamp.isoformat()} - {text[:50]}... (final={is_final})")
    
    def end_session(self):
        """End the current session and save logs to file"""
        if not self.session_start_time:
            return None
        
        end_time = datetime.now()
        total_duration_ms = int((end_time - self.session_start_time).total_seconds() * 1000)
        
        session_summary = {
            "session_start": self.session_start_time.isoformat(),
            "session_end": end_time.isoformat(),
            "total_duration_ms": total_duration_ms,
            "logs": self.session_logs
        }
        
        # Save to file
        log_filename = f"session_{self.session_start_time.strftime('%Y%m%d_%H%M%S')}.json"
        log_path = os.path.join(self.log_dir, log_filename)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(session_summary, f, indent=2, ensure_ascii=False)
        
        print(f"[Logger] Session ended. Log saved to {log_path}")
        
        return session_summary
    
    def get_session_logs(self):
        """Get current session logs"""
        return self.session_logs.copy()
