"""
Streaming Recognition Engine - Member 3
Core recognition loop: queue → model → output
"""
import time
import threading


class StreamingEngine:
    """
    Main streaming recognition engine
    Processes audio from queue through model and emits results
    """
    
    def __init__(self, audio_queue, model_loader, result_handler, logger):
        """
        Initialize streaming engine
        
        Args:
            audio_queue: AudioQueue instance from Member 2
            model_loader: ModelLoader instance from Member 1
            result_handler: ResultHandler instance
            logger: Logger instance
        """
        self.audio_queue = audio_queue
        self.model_loader = model_loader
        self.result_handler = result_handler
        self.logger = logger
        
        self.is_running = False
        self.engine_thread = None
        
        # Event callbacks
        self.on_partial_callback = None
        self.on_final_callback = None
        self.on_session_end_callback = None
        
        # CPU efficiency delay (seconds)
        self.loop_delay = 0.1
    
    def on_partial(self, callback):
        """Register callback for partial results"""
        self.on_partial_callback = callback
    
    def on_final(self, callback):
        """Register callback for final results"""
        self.on_final_callback = callback
    
    def on_session_end(self, callback):
        """Register callback for session end"""
        self.on_session_end_callback = callback
    
    def start(self):
        """Start the streaming recognition engine"""
        if self.is_running:
            print("[Engine] Already running")
            return
        
        self.is_running = True
        self.result_handler.reset()
        self.logger.start_session()
        
        self.engine_thread = threading.Thread(target=self._recognition_loop)
        self.engine_thread.start()
        
        print("[Engine] Streaming engine started")
    
    def stop(self):
        """Stop the streaming recognition engine"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.engine_thread:
            self.engine_thread.join()
        
        # Get final accumulated text
        final_text = self.result_handler.get_accumulated_text()
        
        # End logging session
        session_summary = self.logger.end_session()
        
        # Emit session end event
        if self.on_session_end_callback and session_summary:
            summary = {
                "recognized_text": final_text,
                "total_processing_time_ms": session_summary.get("total_duration_ms", 0)
            }
            self.on_session_end_callback(summary)
        
        print("[Engine] Streaming engine stopped")
    
    def _recognition_loop(self):
        """
        Main recognition loop
        Continuously processes audio chunks from queue
        """
        print("[Engine] Recognition loop started")
        
        while self.is_running:
            # Get audio chunk from queue
            audio_chunk = self.audio_queue.get()
            
            if audio_chunk is None:
                # No audio available, apply CPU efficiency delay
                time.sleep(self.loop_delay)
                continue
            
            try:
                # Process audio through model
                recognition_result = self.model_loader.recognize(audio_chunk)
                
                # Process result (partial vs final detection)
                processed_result = self.result_handler.process_result(recognition_result)
                
                if processed_result:
                    result_type = processed_result["type"]
                    text = processed_result["text"]
                    
                    # Log the result
                    self.logger.log_recognition(text, is_final=(result_type == "final"))
                    
                    # Emit appropriate event
                    if result_type == "partial" and self.on_partial_callback:
                        self.on_partial_callback(text)
                    elif result_type == "final" and self.on_final_callback:
                        self.on_final_callback(text)
            
            except Exception as e:
                print(f"[Engine] Recognition error: {e}")
            
            # CPU efficiency delay
            time.sleep(self.loop_delay)
        
        print("[Engine] Recognition loop ended")
