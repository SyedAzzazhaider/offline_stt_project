"""
Unit tests for Result Handler module - Member 3
"""
import pytest
from src.member_3_engine.result_handler import ResultHandler


class TestResultHandler:
    """Test suite for ResultHandler class"""
    
    def test_initialization(self):
        """Test result handler initializes correctly"""
        handler = ResultHandler()
        
        assert handler.last_partial == ""
        assert handler.accumulated_text == ""
    
    def test_process_final_result(self):
        """Test processing final result"""
        handler = ResultHandler()
        
        result = handler.process_result({
            "partial": "",
            "final": "یہ ایک ٹیسٹ ہے"
        })
        
        assert result is not None
        assert result["type"] == "final"
        assert result["text"] == "یہ ایک ٹیسٹ ہے"
        assert handler.accumulated_text == "یہ ایک ٹیسٹ ہے"
    
    def test_process_partial_result(self):
        """Test processing partial result"""
        handler = ResultHandler()
        
        result = handler.process_result({
            "partial": "یہ ایک",
            "final": ""
        })
        
        assert result is not None
        assert result["type"] == "partial"
        assert result["text"] == "یہ ایک"
        assert handler.last_partial == "یہ ایک"
    
    def test_ignore_duplicate_partial(self):
        """Test that duplicate partial results are ignored"""
        handler = ResultHandler()
        
        # First partial
        result1 = handler.process_result({
            "partial": "یہ ایک",
            "final": ""
        })
        assert result1 is not None
        
        # Same partial again
        result2 = handler.process_result({
            "partial": "یہ ایک",
            "final": ""
        })
        assert result2 is None
    
    def test_process_empty_result(self):
        """Test processing empty result"""
        handler = ResultHandler()
        
        result = handler.process_result({
            "partial": "",
            "final": ""
        })
        
        assert result is None
    
    def test_process_none_result(self):
        """Test processing None result"""
        handler = ResultHandler()
        
        result = handler.process_result(None)
        assert result is None
    
    def test_accumulated_text_multiple_finals(self):
        """Test accumulation of multiple final results"""
        handler = ResultHandler()
        
        handler.process_result({"partial": "", "final": "first"})
        handler.process_result({"partial": "", "final": "second"})
        handler.process_result({"partial": "", "final": "third"})
        
        accumulated = handler.get_accumulated_text()
        assert "first" in accumulated
        assert "second" in accumulated
        assert "third" in accumulated
    
    def test_partial_cleared_after_final(self):
        """Test that partial is cleared after final result"""
        handler = ResultHandler()
        
        # Set partial
        handler.process_result({"partial": "partial text", "final": ""})
        assert handler.last_partial == "partial text"
        
        # Process final
        handler.process_result({"partial": "", "final": "final text"})
        assert handler.last_partial == ""
    
    def test_reset(self):
        """Test reset functionality"""
        handler = ResultHandler()
        
        handler.process_result({"partial": "partial", "final": ""})
        handler.process_result({"partial": "", "final": "final"})
        
        handler.reset()
        
        assert handler.last_partial == ""
        assert handler.accumulated_text == ""
    
    def test_whitespace_handling(self):
        """Test that whitespace is properly stripped"""
        handler = ResultHandler()
        
        result = handler.process_result({
            "partial": "  text with spaces  ",
            "final": ""
        })
        
        assert result["text"] == "text with spaces"
