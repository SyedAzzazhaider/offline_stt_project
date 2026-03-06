"""
Integration test for Member 3 components
Tests the full pipeline: audio queue → model → engine → session controller
"""
import pytest
import time
from unittest.mock import Mock
from src.member_3_engine.streaming_engine import StreamingEngine
from src.member_3_engine.session_controller import SessionController
from src.member_3_engine.result_handler import ResultHandler
from src.member_3_engine.logger import Logger


class TestMember3Integration:
    """Integration tests for Member 3 complete pipeline"""
    
    @pytest.fixture
    def mock_audio_queue(self):
        """Mock audio queue that provides test audio"""
        queue = Mock()
        # Simulate audio chunks
        audio_chunks = [b'\x00\x01' * 1000, b'\x00\x01' * 1000, None, None]
        queue.get = Mock(side_effect=audio_chunks)
        return queue
    
    @pytest.fixture
    def mock_model_loader(self):
        """Mock model that returns test results"""
        model = Mock()
        # Simulate recognition results
        results = [
            {"partial": "یہ", "final": ""},
            {"partial": "", "final": "یہ ایک ٹیسٹ ہے"}
        ]
        model.recognize = Mock(side_effect=results)
        return model
    
    @pytest.fixture
    def mock_audio_capture(self):
        """Mock audio capture"""
        capture = Mock()
        capture.start_stream = Mock()
        capture.stop_stream = Mock()
        return capture
    
    def test_full_pipeline_integration(self, tmp_path, mock_audio_queue, 
                                       mock_model_loader, mock_audio_capture):
        """Test complete Member 3 pipeline integration"""
        # Setup components
        result_handler = ResultHandler()
        logger = Logger(log_dir=str(tmp_path / "test_logs"))
        
        streaming_engine = StreamingEngine(
            mock_audio_queue,
            mock_model_loader,
            result_handler,
            logger
        )
        
        session_controller = SessionController(
            streaming_engine,
            mock_audio_capture
        )
        
        # Track events
        partial_results = []
        final_results = []
        session_end_data = []
        
        streaming_engine.on_partial(lambda text: partial_results.append(text))
        streaming_engine.on_final(lambda text: final_results.append(text))
        streaming_engine.on_session_end(lambda summary: session_end_data.append(summary))
        
        # Initialize and start session
        assert session_controller.initialize() is True
        assert session_controller.start_session() is True
        assert session_controller.is_session_active() is True
        
        # Let it run
        time.sleep(0.5)
        
        # Stop session
        assert session_controller.stop_session() is True
        assert session_controller.is_session_active() is False
        
        # Verify results
        assert len(partial_results) > 0 or len(final_results) > 0
        assert len(session_end_data) == 1
        
        # Verify session end summary
        summary = session_end_data[0]
        assert "recognized_text" in summary
        assert "total_processing_time_ms" in summary
        
        print(f"Partial results: {partial_results}")
        print(f"Final results: {final_results}")
        print(f"Session summary: {summary}")
    
    def test_session_timing(self, tmp_path, mock_audio_queue, 
                           mock_model_loader, mock_audio_capture):
        """Test session timing tracking"""
        result_handler = ResultHandler()
        logger = Logger(log_dir=str(tmp_path / "test_logs"))
        
        streaming_engine = StreamingEngine(
            mock_audio_queue,
            mock_model_loader,
            result_handler,
            logger
        )
        
        session_controller = SessionController(
            streaming_engine,
            mock_audio_capture
        )
        
        # Start session
        session_controller.start_session()
        
        # Check elapsed time increases
        time.sleep(0.1)
        elapsed1 = session_controller.get_elapsed_time()
        
        time.sleep(0.1)
        elapsed2 = session_controller.get_elapsed_time()
        
        assert elapsed2 > elapsed1
        assert elapsed2 >= 100  # At least 100ms
        
        # Stop and check state
        session_controller.stop_session()
        state = session_controller.get_session_state()
        
        assert state["is_active"] is False
        assert "total_time_ms" in state
        assert state["total_time_ms"] >= 200
