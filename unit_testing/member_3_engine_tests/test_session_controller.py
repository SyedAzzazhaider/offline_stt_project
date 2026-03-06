"""
Unit tests for Session Controller - Member 3
"""
import pytest
import time
from unittest.mock import Mock, MagicMock
from src.member_3_engine.session_controller import SessionController


class TestSessionController:
    """Test suite for SessionController class"""
    
    @pytest.fixture
    def mock_streaming_engine(self):
        """Create mock streaming engine"""
        engine = Mock()
        engine.start = Mock()
        engine.stop = Mock()
        return engine
    
    @pytest.fixture
    def mock_audio_capture(self):
        """Create mock audio capture"""
        capture = Mock()
        capture.start_stream = Mock()
        capture.stop_stream = Mock()
        return capture
    
    @pytest.fixture
    def controller(self, mock_streaming_engine, mock_audio_capture):
        """Create session controller with mocks"""
        return SessionController(mock_streaming_engine, mock_audio_capture)
    
    def test_initialization(self, controller):
        """Test controller initializes correctly"""
        assert controller.is_active is False
        assert controller.session_start_time is None
        assert controller.session_end_time is None
    
    def test_initialize(self, controller):
        """Test initialize method"""
        result = controller.initialize()
        assert result is True
    
    def test_start_session(self, controller, mock_audio_capture, mock_streaming_engine):
        """Test starting a session"""
        result = controller.start_session()
        
        assert result is True
        assert controller.is_active is True
        assert controller.session_start_time is not None
        
        # Verify audio capture and engine were started
        mock_audio_capture.start_stream.assert_called_once()
        mock_streaming_engine.start.assert_called_once()
    
    def test_start_session_when_already_active(self, controller):
        """Test starting session when already active"""
        controller.start_session()
        result = controller.start_session()
        
        assert result is False
    
    def test_stop_session(self, controller, mock_audio_capture, mock_streaming_engine):
        """Test stopping a session"""
        controller.start_session()
        time.sleep(0.01)
        result = controller.stop_session()
        
        assert result is True
        assert controller.is_active is False
        assert controller.session_end_time is not None
        
        # Verify audio capture and engine were stopped
        mock_audio_capture.stop_stream.assert_called_once()
        mock_streaming_engine.stop.assert_called_once()
    
    def test_stop_session_when_not_active(self, controller):
        """Test stopping session when not active"""
        result = controller.stop_session()
        assert result is False
    
    def test_get_session_state_inactive(self, controller):
        """Test getting state when session is inactive"""
        state = controller.get_session_state()
        
        assert state["is_active"] is False
        assert state["start_time"] is None
        assert state["end_time"] is None
    
    def test_get_session_state_active(self, controller):
        """Test getting state when session is active"""
        controller.start_session()
        time.sleep(0.01)
        state = controller.get_session_state()
        
        assert state["is_active"] is True
        assert state["start_time"] is not None
        assert "elapsed_time_ms" in state
        assert state["elapsed_time_ms"] > 0
    
    def test_get_session_state_completed(self, controller):
        """Test getting state after session completed"""
        controller.start_session()
        time.sleep(0.01)
        controller.stop_session()
        
        state = controller.get_session_state()
        
        assert state["is_active"] is False
        assert "total_time_ms" in state
        assert state["total_time_ms"] > 0
    
    def test_get_elapsed_time_no_session(self, controller):
        """Test elapsed time when no session"""
        elapsed = controller.get_elapsed_time()
        assert elapsed == 0
    
    def test_get_elapsed_time_active_session(self, controller):
        """Test elapsed time during active session"""
        controller.start_session()
        time.sleep(0.05)
        
        elapsed = controller.get_elapsed_time()
        assert elapsed >= 50  # At least 50ms
    
    def test_is_session_active(self, controller):
        """Test session active check"""
        assert controller.is_session_active() is False
        
        controller.start_session()
        assert controller.is_session_active() is True
        
        controller.stop_session()
        assert controller.is_session_active() is False
    
    def test_start_session_error_handling(self, mock_streaming_engine, mock_audio_capture):
        """Test error handling during session start"""
        mock_audio_capture.start_stream = Mock(side_effect=Exception("Audio error"))
        controller = SessionController(mock_streaming_engine, mock_audio_capture)
        
        result = controller.start_session()
        
        assert result is False
        assert controller.is_active is False
    
    def test_stop_session_error_handling(self, mock_streaming_engine, mock_audio_capture):
        """Test error handling during session stop"""
        controller = SessionController(mock_streaming_engine, mock_audio_capture)
        controller.start_session()
        
        mock_audio_capture.stop_stream = Mock(side_effect=Exception("Stop error"))
        result = controller.stop_session()
        
        assert result is False
