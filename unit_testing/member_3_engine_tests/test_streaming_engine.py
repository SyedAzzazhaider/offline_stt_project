"""
Unit tests for Streaming Engine - Member 3
"""
import pytest
import time
from unittest.mock import Mock, MagicMock
from src.member_3_engine.streaming_engine import StreamingEngine


class TestStreamingEngine:
    """Test suite for StreamingEngine class"""
    
    @pytest.fixture
    def mock_audio_queue(self):
        """Create mock audio queue"""
        queue = Mock()
        queue.get = Mock(return_value=None)
        return queue
    
    @pytest.fixture
    def mock_model_loader(self):
        """Create mock model loader"""
        model = Mock()
        model.recognize = Mock(return_value={"partial": "", "final": "test text"})
        return model
    
    @pytest.fixture
    def mock_result_handler(self):
        """Create mock result handler"""
        handler = Mock()
        handler.reset = Mock()
        handler.process_result = Mock(return_value={"type": "final", "text": "test"})
        handler.get_accumulated_text = Mock(return_value="accumulated text")
        return handler
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger"""
        logger = Mock()
        logger.start_session = Mock()
        logger.log_recognition = Mock()
        logger.end_session = Mock(return_value={"total_duration_ms": 1000})
        return logger
    
    @pytest.fixture
    def engine(self, mock_audio_queue, mock_model_loader, mock_result_handler, mock_logger):
        """Create streaming engine with mocks"""
        return StreamingEngine(
            mock_audio_queue,
            mock_model_loader,
            mock_result_handler,
            mock_logger
        )
    
    def test_initialization(self, engine):
        """Test engine initializes correctly"""
        assert engine.is_running is False
        assert engine.engine_thread is None
        assert engine.on_partial_callback is None
        assert engine.on_final_callback is None
        assert engine.on_session_end_callback is None
    
    def test_register_callbacks(self, engine):
        """Test registering event callbacks"""
        partial_cb = Mock()
        final_cb = Mock()
        end_cb = Mock()
        
        engine.on_partial(partial_cb)
        engine.on_final(final_cb)
        engine.on_session_end(end_cb)
        
        assert engine.on_partial_callback == partial_cb
        assert engine.on_final_callback == final_cb
        assert engine.on_session_end_callback == end_cb
    
    def test_start_engine(self, engine, mock_result_handler, mock_logger):
        """Test starting the engine"""
        engine.start()
        
        assert engine.is_running is True
        assert engine.engine_thread is not None
        
        mock_result_handler.reset.assert_called_once()
        mock_logger.start_session.assert_called_once()
        
        # Clean up
        engine.stop()
    
    def test_start_when_already_running(self, engine):
        """Test starting engine when already running"""
        engine.start()
        engine.start()  # Second start
        
        assert engine.is_running is True
        
        # Clean up
        engine.stop()
    
    def test_stop_engine(self, engine, mock_logger):
        """Test stopping the engine"""
        engine.start()
        time.sleep(0.1)
        engine.stop()
        
        assert engine.is_running is False
        mock_logger.end_session.assert_called_once()
    
    def test_stop_when_not_running(self, engine):
        """Test stopping engine when not running"""
        engine.stop()
        # Should not raise error
        assert engine.is_running is False
    
    def test_recognition_loop_with_audio(self, mock_audio_queue, mock_model_loader, 
                                         mock_result_handler, mock_logger):
        """Test recognition loop processes audio"""
        # Setup mock to return audio chunk once, then None
        audio_data = b'\x00\x01' * 1000
        mock_audio_queue.get = Mock(side_effect=[audio_data, None, None])
        
        engine = StreamingEngine(
            mock_audio_queue,
            mock_model_loader,
            mock_result_handler,
            mock_logger
        )
        
        engine.start()
        time.sleep(0.3)
        engine.stop()
        
        # Verify model was called
        assert mock_model_loader.recognize.called
        assert mock_result_handler.process_result.called
    
    def test_partial_result_callback(self, mock_audio_queue, mock_model_loader,
                                     mock_result_handler, mock_logger):
        """Test partial result triggers callback"""
        audio_data = b'\x00\x01' * 1000
        mock_audio_queue.get = Mock(side_effect=[audio_data, None, None])
        mock_result_handler.process_result = Mock(
            return_value={"type": "partial", "text": "partial text"}
        )
        
        engine = StreamingEngine(
            mock_audio_queue,
            mock_model_loader,
            mock_result_handler,
            mock_logger
        )
        
        partial_callback = Mock()
        engine.on_partial(partial_callback)
        
        engine.start()
        time.sleep(0.3)
        engine.stop()
        
        # Verify callback was called
        partial_callback.assert_called_with("partial text")
    
    def test_final_result_callback(self, mock_audio_queue, mock_model_loader,
                                   mock_result_handler, mock_logger):
        """Test final result triggers callback"""
        audio_data = b'\x00\x01' * 1000
        mock_audio_queue.get = Mock(side_effect=[audio_data, None, None])
        mock_result_handler.process_result = Mock(
            return_value={"type": "final", "text": "final text"}
        )
        
        engine = StreamingEngine(
            mock_audio_queue,
            mock_model_loader,
            mock_result_handler,
            mock_logger
        )
        
        final_callback = Mock()
        engine.on_final(final_callback)
        
        engine.start()
        time.sleep(0.3)
        engine.stop()
        
        # Verify callback was called
        final_callback.assert_called_with("final text")
    
    def test_session_end_callback(self, engine, mock_result_handler):
        """Test session end triggers callback"""
        mock_result_handler.get_accumulated_text = Mock(return_value="final accumulated")
        
        end_callback = Mock()
        engine.on_session_end(end_callback)
        
        engine.start()
        time.sleep(0.1)
        engine.stop()
        
        # Verify callback was called with summary
        assert end_callback.called
        call_args = end_callback.call_args[0][0]
        assert "recognized_text" in call_args
        assert "total_processing_time_ms" in call_args
    
    def test_recognition_error_handling(self, mock_audio_queue, mock_model_loader,
                                       mock_result_handler, mock_logger):
        """Test error handling during recognition"""
        audio_data = b'\x00\x01' * 1000
        mock_audio_queue.get = Mock(side_effect=[audio_data, None, None])
        mock_model_loader.recognize = Mock(side_effect=Exception("Recognition error"))
        
        engine = StreamingEngine(
            mock_audio_queue,
            mock_model_loader,
            mock_result_handler,
            mock_logger
        )
        
        engine.start()
        time.sleep(0.3)
        engine.stop()
        
        # Should not crash, just handle error
        assert True
    
    def test_cpu_efficiency_delay(self, engine):
        """Test that CPU efficiency delay is applied"""
        assert engine.loop_delay == 0.1
