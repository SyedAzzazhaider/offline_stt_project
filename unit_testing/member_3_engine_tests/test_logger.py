"""
Unit tests for Logger module - Member 3
"""
import pytest
import os
import json
import time
from src.member_3_engine.logger import Logger


class TestLogger:
    """Test suite for Logger class"""
    
    def test_logger_initialization(self, tmp_path):
        """Test logger initializes correctly"""
        log_dir = str(tmp_path / "test_logs")
        logger = Logger(log_dir=log_dir)
        
        assert logger.log_dir == log_dir
        assert logger.session_logs == []
        assert logger.session_start_time is None
        assert os.path.exists(log_dir)
    
    def test_start_session(self, tmp_path):
        """Test session start"""
        logger = Logger(log_dir=str(tmp_path / "test_logs"))
        logger.start_session()
        
        assert logger.session_start_time is not None
        assert logger.session_logs == []
    
    def test_log_recognition(self, tmp_path):
        """Test logging recognition results"""
        logger = Logger(log_dir=str(tmp_path / "test_logs"))
        logger.start_session()
        
        # Log partial result
        logger.log_recognition("یہ ایک", is_final=False)
        assert len(logger.session_logs) == 1
        assert logger.session_logs[0]["recognized_text"] == "یہ ایک"
        assert logger.session_logs[0]["is_final"] is False
        
        # Log final result
        time.sleep(0.01)  # Small delay to ensure different duration
        logger.log_recognition("یہ ایک ٹیسٹ ہے", is_final=True)
        assert len(logger.session_logs) == 2
        assert logger.session_logs[1]["is_final"] is True
    
    def test_log_without_session(self, tmp_path):
        """Test logging without starting session"""
        logger = Logger(log_dir=str(tmp_path / "test_logs"))
        logger.log_recognition("test", is_final=False)
        
        # Should not log anything
        assert len(logger.session_logs) == 0
    
    def test_end_session(self, tmp_path):
        """Test session end and file creation"""
        log_dir = str(tmp_path / "test_logs")
        logger = Logger(log_dir=log_dir)
        logger.start_session()
        
        logger.log_recognition("test text", is_final=True)
        time.sleep(0.01)
        
        summary = logger.end_session()
        
        assert summary is not None
        assert "session_start" in summary
        assert "session_end" in summary
        assert "total_duration_ms" in summary
        assert "logs" in summary
        assert len(summary["logs"]) == 1
        
        # Check file was created
        log_files = os.listdir(log_dir)
        assert len(log_files) == 1
        assert log_files[0].startswith("session_")
        assert log_files[0].endswith(".json")
    
    def test_end_session_without_start(self, tmp_path):
        """Test ending session without starting"""
        logger = Logger(log_dir=str(tmp_path / "test_logs"))
        summary = logger.end_session()
        
        assert summary is None
    
    def test_get_session_logs(self, tmp_path):
        """Test getting session logs"""
        logger = Logger(log_dir=str(tmp_path / "test_logs"))
        logger.start_session()
        
        logger.log_recognition("text 1", is_final=False)
        logger.log_recognition("text 2", is_final=True)
        
        logs = logger.get_session_logs()
        assert len(logs) == 2
        assert logs[0]["recognized_text"] == "text 1"
        assert logs[1]["recognized_text"] == "text 2"
    
    def test_log_file_format(self, tmp_path):
        """Test log file JSON format"""
        log_dir = str(tmp_path / "test_logs")
        logger = Logger(log_dir=log_dir)
        logger.start_session()
        
        logger.log_recognition("test", is_final=True)
        logger.end_session()
        
        # Read and validate JSON file
        log_files = os.listdir(log_dir)
        log_path = os.path.join(log_dir, log_files[0])
        
        with open(log_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "session_start" in data
        assert "session_end" in data
        assert "total_duration_ms" in data
        assert "logs" in data
        assert isinstance(data["logs"], list)
